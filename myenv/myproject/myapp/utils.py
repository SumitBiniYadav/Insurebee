from .models import ActivityLog

def log_activity(user, action, instance, description=None):
    """
    Log user activity in the database.
    
    Parameters:
    - user: The user performing the action.
    - action: The action being performed (e.g., 'create', 'update', 'delete').
    - entity_type: The type of entity being acted upon (e.g., 'Policy', 'Claim').
    - entity_id: The ID of the entity being acted upon.
    - description: A detailed description of the action.
    """

    model_name = instance.__class__.__name__ #e.g., 'Policy', 'Claim'
    entity_id = instance.id # ID of the entity being acted upon
    
    if not description:
        description = f"{action.capitalize()} {model_name} with ID {entity_id}"

    ActivityLog.objects.create(
        user=user,
        action=action,
        entity_type=model_name,
        entity_id=entity_id,
        description=description
    )
