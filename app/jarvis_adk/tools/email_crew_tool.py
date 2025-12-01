from app.taylor_crew.e_mail_crew.src.graph import WorkFlow

def run_email_workflow() -> str:
    """
    Run the email management workflow to check and draft responses to emails.
    
    Returns:
        str: Status message indicating the workflow has started or completed.
    """
    try:
        app = WorkFlow().app
        # Invoke with empty state as per main.py
        app.invoke({})
        return "Email workflow executed successfully."
    except Exception as e:
        return f"Failed to run email workflow: {str(e)}"
