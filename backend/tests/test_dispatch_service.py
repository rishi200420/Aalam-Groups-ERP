from app.services.dispatch_service import DispatchService


def test_dispatch_transition_validation():
    assert DispatchService.validate_transition("ready", "dispatched") is True
    assert DispatchService.validate_transition("ready", "delivered") is False
    assert DispatchService.validate_transition("dispatched", "in_transit") is True
    assert DispatchService.validate_transition("in_transit", "delivered") is True
    assert DispatchService.validate_transition("delivered", "failed") is False
