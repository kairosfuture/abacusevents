from events import Ping
from events.pubsub import _assert_topic, _assert_subscription, _emit_event, subscribe
from events.utils import env
from google.api_core.exceptions import AlreadyExists
from unittest import TestCase
from unittest.mock import Mock, patch


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

    @patch('events.pubsub.PubSub')
    @patch('events.pubsub.Subscription.get_next', return_value='foo')
    def test_registered_listener_is_called_when_exception_raised(self, __, _):
        subscription = subscribe('sub', 'topic')
        message_mock = Mock()
        message_mock.data.decode = Mock(return_value='foo')
        mock_error_handler = Mock()
        subscription.on('JSONDecodeError', mock_error_handler)

        subscription.q.get = Mock(side_effect=subscription._callback(message_mock))

        mock_error_handler.assert_called_once()
        message_mock.assert_not_called()

    @patch('events.pubsub.PubSub')
    @patch('events.pubsub.Subscription.get_next', return_value='foo')
    def test_it_wont_explode_if_exception_raised_and_no_listener_is_registered(self, __, _):
        subscription = subscribe('sub', 'topic')
        message_mock = Mock()
        message_mock.data.decode = Mock(return_value='{"invalid":"json"}}}}}}')

        subscription.q.get = Mock(side_effect=subscription._callback(message_mock))

        message_mock.data.decode.assert_called_once_with('utf-8')
        message_mock.ack.assert_called_once()
        message_mock.assert_not_called()
        assert subscription.get_next() == 'foo'
