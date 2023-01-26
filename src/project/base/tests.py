from django.test import TestCase

from .models import Room, User, Player


class RoomModelTests(TestCase):
    def setUp(self):
        user = User.objects.create(username="testuser", password="testpassword")
        self.room1 = Room.objects.create(host=user, name="Test Room 1", code="testcode1", online=True)
        self.room2 = Room.objects.create(host=user, name="Test Room 2", code="testcode2", online=False)

    def test_create_room(self):
        user = User.objects.create(username="testuser2", password="testpassword")
        new_room = Room.objects.create(host=user, name="Test Room 3", code="testcode3", online=True)

        self.assertEqual(new_room.name, "Test Room 3")
        self.assertEqual(new_room.code, "testcode3")
        self.assertEqual(new_room.is_online, True)

    def test_update_room(self):
        self.room1.name = "Updated Test Room 1"
        self.room1.code = "updatedtestcode1"
        self.room1.is_online = False
        self.room1.save()

        self.assertEqual(self.room1.name, "Updated Test Room 1")
        self.assertEqual(self.room1.code, "updatedtestcode1")
        self.assertEqual(self.room1.is_online, False)

    def test_delete_room(self):
        self.room1.delete()
        self.assertEqual(Room.objects.count(), 1)

    def test_join_room(self):
        test_user = User.objects.create(username='testuser3')
        Player.objects.filter(user=test_user).delete()
        test_player = Player.objects.create(user=test_user)

        self.room1.players.add(test_player)
        self.assertIn(test_player, self.room1.players.all())

    def test_leave_room(self):
        test_user = User.objects.create_user(username="testuser4", password="testpassword")
        Player.objects.filter(user=test_user).delete()
        test_player = Player.objects.create(user=test_user)

        self.room1.players.add(test_player)
        self.assertIn(test_player, self.room1.players.all())

        self.room1.players.remove(test_player)
        self.assertNotIn(test_player, self.room1.players.all())

# class GameModelTests(TestCase):
#     def setUp(self):
#
#     def test_create_game(self):
#
#     def test_update_game(self):
#
#
#     def test_delete_game(self):
#
#
#     def test_play_round(self):
#
#
#     def test_check_if_game_is_done(self):
#
#
# class UserModelTests(TestCase):
#     def setUp(self):
#
#     def test_create_user(self):
#
#     def test_update_user(self):
#
#     def test_delete_user(self):
#
#     def test_authenticate_user(self):
#
#     def test_login_user(self):
#
#     def test_logout_user(self):
