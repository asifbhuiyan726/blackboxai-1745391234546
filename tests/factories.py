import random
from datetime import timedelta
from typing import Any, List, Optional

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory import Faker, LazyAttribute, LazyFunction, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as FakerClass

from accounts.models import UserAchievement, UserConnection, UserStreak
from chat.models import ChatMessage, ChatNotification, ChatReaction
from events.models import Event, EventParticipant, EventReminder
from feed.models import Comment, Post, PollOption, Reaction, Vote
from icebreaker.models import (
    IcebreakerCategory, IcebreakerQuestion, IcebreakerResponse,
    IcebreakerSession, SessionQuestion
)
from pairing.models import PairingMatch, PairingPreference, PairingRequest
from rooms.models import Room, RoomMembership, RoomMessage, MessageReaction
from status.models import Status, UserStatus

fake = FakerClass()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
    date_joined = Faker('date_time_this_year', tzinfo=timezone.utc)

    @factory.post_generation
    def groups(self, create: bool, extracted: Optional[List[Any]], **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)

class StatusFactory(DjangoModelFactory):
    class Meta:
        model = Status

    name = factory.Sequence(lambda n: f'Status {n}')
    code = factory.Sequence(lambda n: f'status_{n}')
    icon = 'fa-circle'
    color = 'text-green-500'
    priority = factory.Sequence(lambda n: n * 10)
    is_available = True

class UserStatusFactory(DjangoModelFactory):
    class Meta:
        model = UserStatus

    user = SubFactory(UserFactory)
    status = SubFactory(StatusFactory)
    custom_message = Faker('sentence')
    started_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    is_current = True

class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room

    title = Faker('company')
    description = Faker('text')
    room_type = 'public'
    icon_url = Faker('image_url')
    is_official = False
    created_by = SubFactory(UserFactory)
    max_members = random.randint(5, 50)

class RoomMembershipFactory(DjangoModelFactory):
    class Meta:
        model = RoomMembership

    user = SubFactory(UserFactory)
    room = SubFactory(RoomFactory)
    role = 'member'
    joined_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = Faker('sentence')
    description = Faker('paragraph')
    event_type = factory.Iterator(['social', 'game', 'learning', 'wellness'])
    start_time = LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_time = LazyFunction(lambda: timezone.now() + timedelta(days=1, hours=2))
    location = Faker('address')
    is_virtual = True
    join_url = Faker('url')
    created_by = SubFactory(UserFactory)

class EventParticipantFactory(DjangoModelFactory):
    class Meta:
        model = EventParticipant

    event = SubFactory(EventFactory)
    user = SubFactory(UserFactory)
    rsvp_status = 'yes'
    reminder_enabled = True

class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = SubFactory(UserFactory)
    content = Faker('paragraph')
    post_type = 'text'
    visibility = 'public'
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class PollOptionFactory(DjangoModelFactory):
    class Meta:
        model = PollOption

    post = SubFactory(PostFactory, post_type='poll')
    text = Faker('sentence')
    order = factory.Sequence(lambda n: n)

class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    post = SubFactory(PostFactory)
    author = SubFactory(UserFactory)
    content = Faker('paragraph')
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class ChatMessageFactory(DjangoModelFactory):
    class Meta:
        model = ChatMessage

    room = SubFactory(RoomFactory)
    sender = SubFactory(UserFactory)
    content = Faker('paragraph')
    message_type = 'text'
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class PairingRequestFactory(DjangoModelFactory):
    class Meta:
        model = PairingRequest

    user = SubFactory(UserFactory)
    status = 'pending'
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    expires_at = LazyAttribute(lambda o: o.created_at + timedelta(minutes=30))

class PairingMatchFactory(DjangoModelFactory):
    class Meta:
        model = PairingMatch

    request = SubFactory(PairingRequestFactory)
    matched_user = SubFactory(UserFactory)
    meeting_time = LazyFunction(lambda: timezone.now() + timedelta(minutes=5))
    meeting_duration = 30
    meeting_format = 'video'

class IcebreakerCategoryFactory(DjangoModelFactory):
    class Meta:
        model = IcebreakerCategory

    name = Faker('word')
    description = Faker('sentence')
    icon = 'fa-comments'
    order = factory.Sequence(lambda n: n)

class IcebreakerQuestionFactory(DjangoModelFactory):
    class Meta:
        model = IcebreakerQuestion

    category = SubFactory(IcebreakerCategoryFactory)
    question_text = Faker('sentence')
    difficulty = factory.Iterator(['easy', 'medium', 'deep'])
    created_by = SubFactory(UserFactory)

class IcebreakerSessionFactory(DjangoModelFactory):
    class Meta:
        model = IcebreakerSession

    session_type = factory.Iterator(['pairing', 'room', 'event'])
    started_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    is_active = True

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for participant in extracted:
                self.participants.add(participant)

class UserAchievementFactory(DjangoModelFactory):
    class Meta:
        model = UserAchievement

    user = SubFactory(UserFactory)
    achievement_type = factory.Iterator(['break_streak', 'pairing', 'engagement'])
    title = Faker('sentence')
    description = Faker('paragraph')
    icon = 'fa-trophy'
    level = factory.Sequence(lambda n: n + 1)
    progress = random.randint(0, 100)
    target = 100

class UserConnectionFactory(DjangoModelFactory):
    class Meta:
        model = UserConnection

    requester = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)
    status = 'pending'
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class UserStreakFactory(DjangoModelFactory):
    class Meta:
        model = UserStreak

    user = SubFactory(UserFactory)
    streak_type = factory.Iterator(['daily_break', 'pairing', 'contribution'])
    current_streak = random.randint(1, 30)
    longest_streak = LazyAttribute(lambda o: max(o.current_streak, random.randint(30, 60)))
    last_activity = Faker('date_time_this_year', tzinfo=timezone.utc)

class ChatReactionFactory(DjangoModelFactory):
    class Meta:
        model = ChatReaction

    message = SubFactory(ChatMessageFactory)
    user = SubFactory(UserFactory)
    emoji = factory.Iterator(['👍', '❤️', '😄', '🎉', '👏'])
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class ChatNotificationFactory(DjangoModelFactory):
    class Meta:
        model = ChatNotification

    user = SubFactory(UserFactory)
    message = SubFactory(ChatMessageFactory)
    notification_type = factory.Iterator(['mention', 'reply', 'reaction'])
    is_read = False
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class EventReminderFactory(DjangoModelFactory):
    class Meta:
        model = EventReminder

    participant = SubFactory(EventParticipantFactory)
    reminder_time = LazyFunction(lambda: timezone.now() + timedelta(minutes=15))
    sent = False
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

class PairingPreferenceFactory(DjangoModelFactory):
    class Meta:
        model = PairingPreference

    user = SubFactory(UserFactory)
    meeting_preference = factory.Iterator(['video', 'audio', 'chat', 'any'])
    timezone_preference = factory.Iterator(['exact', 'adjacent', 'any'])
    preferred_duration = factory.Iterator([15, 30, 45, 60])
    is_active = True
    last_updated = Faker('date_time_this_year', tzinfo=timezone.utc)

    @factory.post_generation
    def interests(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for interest in extracted:
                self.interests.add(interest)

class ReactionFactory(DjangoModelFactory):
    class Meta:
        model = Reaction

    user = SubFactory(UserFactory)
    emoji = factory.Iterator(['👍', '❤️', '😄', '🎉', '👏'])
    reaction_type = factory.Iterator(['post', 'comment'])
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

    @factory.post_generation
    def target(self, create, extracted, **kwargs):
        if not create:
            return
        if self.reaction_type == 'post':
            self.post = extracted or PostFactory()
        else:
            self.comment = extracted or CommentFactory()

class VoteFactory(DjangoModelFactory):
    class Meta:
        model = Vote

    user = SubFactory(UserFactory)
    option = SubFactory(PollOptionFactory)
    voted_at = Faker('date_time_this_year', tzinfo=timezone.utc)
