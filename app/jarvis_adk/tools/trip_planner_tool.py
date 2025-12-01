from app.taylor_crew.trip_planner.main import TripCrew

def plan_trip(origin: str, cities: str, date_range: str, interests: str) -> str:
    """
    Plan a trip using the Taylor Crew AI agents.
    
    Args:
        origin (str): The city you are traveling from.
        cities (str): The cities you are interested in visiting.
        date_range (str): The date range for the trip (e.g., "Nov 2023").
        interests (str): Your interests and hobbies.
        
    Returns:
        str: The detailed trip plan.
    """
    try:
        crew = TripCrew(origin, cities, date_range, interests)
        result = crew.run()
        return str(result)
    except Exception as e:
        return f"Failed to plan trip: {str(e)}"
