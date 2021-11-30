from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from flask_table import Table, Col
from datetime import datetime as dt


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [
                Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                Permission.MODERATE
            ],
            'Administrator': [
                Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                Permission.MODERATE, Permission.ADMIN
            ],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'change_email': self.id,
            'new_email': new_email
        }).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


def num_admin_users():
    num_admin = len(User.query.filter_by(admin=True, active=True).all())
    print('number of admin = ', num_admin)
    return num_admin


def set_active(email):
    user = User.query.filter_by(email=email).first()
    user.active = True
    db.session.commit()


def de_active(user):
    user.active = False
    db.session.commit()


def to_json(all_vendors):
    # for ven in all_vendors:
    #     print(f'@to_json, ven.double_to_dict() = {ven.double_to_dict()}')
    v = [ven.double_to_dict() for ven in all_vendors]
    return v


def insert_records(record):
    """Insert MQTT data to database

    Parameters
    ----------
    records : list of dict
        Each dict represents WISE 2410 Vib data
    """
    row_data = WISE_Accel_Model(info_id=record['info_id'],
                                X_Axis=record['Accelerometer']['X-Axis'],
                                Y_Axis=record['Accelerometer']['Y-Axis'],
                                Z_Axis=record['Accelerometer']['Z-Axis'],
                                LogIndex=record['Accelerometer']['LogIndex'],
                                Timestamp=record['Accelerometer']['Timestamp'],
                                Device=record['Device'],
                                created_at=dt.now())

    db.session.add(row_data)
    db.session.commit()


def insert_information_info(info_record):
    """Insert Exp Record to the exp_table

    Parameters
    ----------
    exp_record : dict
        the dict contain info about the current experiment (exp_id, inspector, model, serial, inspection date)
    """
    info_record = Information_Model(id=info_record['id'],
                                    inspector=info_record['inspector'],
                                    model=info_record['model'],
                                    serial=info_record['serial'])
    db.session.add(info_record)
    db.session.commit()


class Vib1_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'vib1_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<vib1_table {self.index}>"


class Vib2_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'vib2_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<vib2_table {self.index}>"


class Vib3_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'vib3_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<vib3_table {self.index}>"


class Vib4_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'vib4_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<vib4_table {self.index}>"


class Vib5_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'vib5_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<vib5_table {self.index}>"


class Vib6_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'vib6_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<vib6_table {self.index}>"


class Amp1_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'amp1_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<amp1_table {self.index}>"


class Amp2_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'amp2_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<amp2_table {self.index}>"


class Amp3_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'amp3_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<amp3_table {self.index}>"


class Temp1_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'temp1_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<temp1_table {self.index}>"


class Temp2_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'temp2_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<temp2_table {self.index}>"


class Temp3_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'temp3_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<temp3_table {self.index}>"


class Temp4_Table(db.Model):
    """Exp Table model."""
    __tablename__ = 'temp4_table'

    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer,
                   db.ForeignKey('information_table.id'),
                   nullable=False)
    ch_name = db.Column(db.String())
    value = db.Column(db.LargeBinary  # change the type to BYTEA
                      )
    spec = db.Column(db.Integer)
    sprate = db.Column(db.Integer)
    update_flag = db.Column(db.Boolean)
    time = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1
    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<temp4_table {self.index}>"


class Information_Model(db.Model):
    """Information table model"""
    __tablename__ = 'information_table'

    id = db.Column(db.Integer, primary_key=True)
    inspector = db.Column(db.String())
    model = db.Column(db.String())
    serial = db.Column(db.String())
    rpm = db.Column(db.Integer)
    vib1 = db.Column(db.Boolean)
    vib2 = db.Column(db.Boolean)
    vib3 = db.Column(db.Boolean)
    vib4 = db.Column(db.Boolean)
    vib5 = db.Column(db.Boolean)
    vib6 = db.Column(db.Boolean)
    amp1 = db.Column(db.Boolean)
    amp2 = db.Column(db.Boolean)
    amp3 = db.Column(db.Boolean)
    temp1 = db.Column(db.Boolean)
    temp2 = db.Column(db.Boolean)
    temp3 = db.Column(db.Boolean)
    temp4 = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Single object # 1

    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    # Method single object # 2

    def single_to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Multiple objects
    def double_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = getattr(self, key)
            else:
                result[key] = getattr(self, key)
        return result

    def __repr__(self):
        return f"<information_table {self.index}>"

    def __repr__(self):
        return f"<Information_Model {self.id}>"


class Information_Table(Table):
    id = Col('ID')
    inspector = Col('Inspector')
    model = Col('Model')
    serial = Col('Serial')
    created_at = Col('Created_at')