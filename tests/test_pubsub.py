from unittest import TestCase
from unittest.mock import Mock, patch

from google.api_core.exceptions import AlreadyExists

from events import Ping
from events.pubsub import _assert_topic, _assert_subscription, _emit_event, PubSub, subscribe, Subscription
from events.utils import env


def test_assert_topic_hides_exception_when_topic_already_exists():
    publisher = Mock()
    publisher.create_topic = Mock(side_effect=AlreadyExists('alright'))
    assert _assert_topic('foo.bar', publisher) is None


def test_assert_topic_calls_create_topic_on_the_given_publisher_instance():
    publisher = Mock()
    _assert_topic('foo.bar', publisher)
    publisher.create_topic.assert_called_with('foo.bar')


def tests_assert_subscription_hides_exception_when_subscription_already_exists():
    publisher = Mock()
    subscriber = Mock()
    subscriber.create_subscription = Mock(side_effect=AlreadyExists('alright'))
    assert _assert_subscription('subscription_name', 'foo.bar', publisher, subscriber) is None


def test_assert_subscription_calls_create_subscription_on_the_given_subscriber_instance():
    publisher = Mock()
    subscriber = Mock()
    _assert_subscription('sub.path', 'topic.path', publisher, subscriber)
    subscriber.create_subscription.assert_called_with('sub.path', 'topic.path')


def test_emit_event_calls_the_publisher_with_a_serialized_event():
    publisher = Mock()
    publisher.publish = Mock()
    publisher.topic_path = Mock(return_value='some.topic.path')
    event = Ping(data='baz')
    event.observedAt = 'frozen-time'
    _emit_event(publisher, 'some.topic', event)
    publisher.topic_path.assert_called_once_with(env('GOOGLE_CLOUD_PROJECT'), 'some.topic')
    publisher.publish.assert_called_with('some.topic.path', data=event.serialize())


class PubSubTestCase(TestCase):
    @patch('events.pubsub.PubSub')
    def test_subscribe_returns_a_subscription_instance(self, _):
        subscribe_instance = subscribe('sub', 'topic')
        self.assertEqual(subscribe_instance.__class__.__name__, 'Subscription')

    @patch('events.pubsub.PubSub')
    def test_registering_callbacks_on_the_subscription_instance(self, _):
        subscription = subscribe('sub', 'topic')
        (subscription
         .on('foo', 'bar')
         .on('baz', 'qux'))
        assert subscription.events['foo'] == 'bar'
        assert subscription.events['baz'] == 'qux'
