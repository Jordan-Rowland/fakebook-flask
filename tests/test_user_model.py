import unittest
from app.models import User
import time


class UserModelTestCase(unittest.TestCase):
	
	def test_password(self):
		u = User(password='cat')
		self.assertTrue(u.password_hash is not None)


	def test_no_password(self):
		u = User(password='cat')
		with self.assertraises(AttributeError):
			u.password


	def test_password_verification(self):
		u = User(password='cat')
		self.assertTrue(u.verrify_password('cat'))
		self.assertFalse(u.verrify_password('dog'))


	def test_password_salts_are_random(self):
		u = User(password='cat')
		u2 = User(password='cat')
		self.assertTrue(u.password_hash != u2.password_hash)


	def test_valid_confirmation_token(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token()
		self.assertFalse(u2.confirm(token))


	def test_invalid_confirmation_token(self):
		u1 = User(password='cat')
		u2 = User(password='dog')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		token = u1.generate_confirmation_token()
		self.assertFalse(u2.confirm(token))


	def test_expired_confirmation_token(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		token = u1.generate_confirmation_token(1)
		time.sleep(2)
		self.assertFalse(u.confirm(token))


	# def test_valid_reset_token(self):
	# 	u = User(password='cat')
	# 	db.session.add(u)
	# 	db.session.commit()
	# 	token = u1.generate_confirmation_token()
	# 	self.assertTrue(User.reset_password(token, 'dog'))
 #        self.assertTrue(u.verify_password('dog'))


	# def test_invalid_reset_token(self):
 #        u = User(password='cat')
 #        db.session.add(u)
 #        db.session.commit()
 #        token = u.generate_reset_token()
 #        self.assertFalse(User.reset_password(token + 'a', 'horse'))
 #        self.assertTrue(u.verify_password('cat'))
