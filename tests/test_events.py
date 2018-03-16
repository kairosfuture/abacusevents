import json

from abacusevents import Ping, Pong

mandatory_props = ['sessionId', 'jobId', 'taskId', 'data', 'done', 'observedAt']


def test_event_has_a_set_of_props():
    event = Ping()
    for prop in event.__dict__.keys():
        assert prop in mandatory_props



def test_props_data_is_accepted_in_constructor():
    event = Pong(session_id='foo123', job_id=None, task_id='abc123', data='foobar', done=True)
    assert event.data is 'foobar'
    assert event.taskId is 'abc123'
    assert event.jobId is None
    assert event.sessionId is 'foo123'
    assert event.done is True
    assert '"done": true' in event.serialize()


def test_defaults_are_provided_for_all_props():
    event = Ping()
    values = event.__dict__.values()
    assert len(list(filter(lambda x: x is None, values))) == 4
    assert len(values) == 6
