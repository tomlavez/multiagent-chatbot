import datetime as dt
import os.path
import sqlite3

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API scopes - usando full access por padrão para as tools
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_credentials():
    """
    Obtem as credenciais do calendário
    """
    creds = None
    if os.path.exists("auth/token.json"):
        creds = Credentials.from_authorized_user_file("auth/token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("config/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("auth/token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds

def get_calendar_events(numEvents=5, start_date=None, end_date=None, attendees=[]):
    """
    Search for events in the user's calendar.

    Args:
        numEvents (int): Maximum number of events to search for.
        start_date (str): Start date of the search.
        end_date (str): End date of the search.
        attendees (list): List of participant emails.

    Returns:
        list: List of events found.
    """    

    print("Function called: get_calendar_events")

    try:
        creds = get_calendar_credentials()
        service = build("calendar", "v3", credentials=creds)

        if start_date is None:
            start_date = dt.datetime.now().isoformat()

        if end_date is None:
            end_date = dt.datetime.fromisoformat(start_date) + dt.timedelta(days=30)
            end_date = end_date.isoformat()

        event_list = []

        for attendee in attendees:
            event_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_date + "-03:00",
                    timeMax=end_date + "-03:00",
                    maxResults=numEvents,
                    singleEvents=True,
                    orderBy="startTime",
                    q=attendee,
                )
                .execute()
            )
            events = event_result.get("items", [])
            for event in events:
                attendees = []
                if not event["attendees"]:
                    attendees.append("Only the user is invited to this event.")
                else:
                    for attend in event["attendees"]:
                        attendees.append(attend['email'])

                formatted_event = {
                    "summary": event.get("summary", "Sem título"),
                    "description": event.get("description", "Sem descrição"),
                    "location": event.get("location", "Não informado"),
                    "start": event["start"],
                    "end": event["end"],
                    "attendees": attendees,
                }

                event_list.append(formatted_event)

        return event_list

    # Handle errors
    except HttpError as error:
        return "Erro ao buscar eventos!"

def create_calendar_event(
    summary: str,
    location: str = None,
    description: str = None,
    start=None,
    end=None,
    attendees=[]
):
    """
    Create an event in the user's calendar.

    Args:
        summary (str): Event title.
        location (str): Event location.
        description (str): Event description.
        start (str): Event start date and time.
        end (str): Event end date and time.
        attendees (list): List of participant emails.

    Returns:
        str: Success or error message.
    """

    print("Function called: create_calendar_event")

    if start is None:
        start = dt.datetime.now().isoformat()

    if end is None:
        start_datetime = dt.datetime.fromisoformat(start)
        end_datetime = start_datetime + dt.timedelta(hours=3)
        end = end_datetime.isoformat()

    if description is None:
        description = summary

    if location is None:
        location = "Não informado"

    if attendees == []:
        return "Nenhum convidado adicionado!"

    # Check for conflicts
    conflito = get_calendar_events(start_date=start, end_date=end, attendees=attendees)
    if conflito and len(conflito) > 0:
        return "Conflito de horário detectado! Já existe um evento no horário solicitado."

    # Format attendees
    convidados = []
    for attendee in attendees:
        convidados.append({"email": attendee})

    try:
        creds = get_calendar_credentials()
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start,
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": end,
                "timeZone": "America/Sao_Paulo",
            },
            "attendees": convidados,
        }

        event = service.events().insert(calendarId="primary", body=event).execute()

        res = "✅ Evento criado com sucesso!"
        return res

    # Handle errors
    except HttpError as error:
        msg = str(error)
        return f"❌ Erro ao criar evento: {msg}"

def current_time_tool():
    """
    Get current time in RFC3339 format
    """

    print("Function called: current_time_tool")
    
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def time_delta_tool(delta_days: int = 0, delta_hours: int = 0, delta_minutes: int = 0, delta_seconds: int = 0):
    """
    Calculates the current date and time plus a time interval.

    Args:
        delta_days (int): Number of days to be added.
        delta_hours (int): Number of hours to be added.
        delta_minutes (int): Number of minutes to be added.
        delta_seconds (int): Number of seconds to be added.

    Returns:
        str: Date and time in RFC3339 format after adding the interval.
    """

    print("Function called: time_delta_tool")

    return (
        dt.datetime.now()
        + dt.timedelta(
            days=delta_days,
            hours=delta_hours,
            minutes=delta_minutes,
            seconds=delta_seconds,
        )
    ).strftime("%Y-%m-%dT%H:%M:%S")

def specific_time_tool(year: int, month: int, day: int, hour: int, minute: int):
    """
    Creates a datetime object for a specific date and time.

    Args:
        year (int): Year.
        month (int): Month.
        day (int): Day.
        hour (int): Hour.
        minute (int): Minute.

    Returns:
        str: Date and time in RFC3339 format.
    """

    print("Function called: specific_time_tool")

    specific_time = dt.datetime(year, month, day, hour, minute)
    
    return specific_time.strftime("%Y-%m-%dT%H:%M:%S")

def get_user_email(username: str):
    """
    Look up a user's email address from the database.

    Args:
        username (str): Username to look up.

    Returns:
        str: Email address or error message.
    """

    print(f"Function called: get_user_email for user {username}")

    username = username.lower()

    conn = sqlite3.connect("database/usuarios.sqlite")
    c = conn.cursor()
    c.execute(
        "SELECT email FROM usuarios WHERE username = ?",
        (username,),
    )
    email = c.fetchone()
    if email:
        print(f"Email found: {email}")
        return email[0]
    else:
        conn.close()
        return "Usuário não encontrado!"

def delete_calendar_event(
    summary: str = None,
    start_date: str = None,
    end_date: str = None,
    attendees: str = None
):
    """
    Delete an event from the user's calendar.

    Args:
        summary (str): Event title to search for.
        start_date (str): Start date to filter events.
        end_date (str): End date to filter events.
        attendees (str): Attendee email to search for.

    Returns:
        str: Success or error message.
    """

    print("Function called: delete_calendar_event")

    # Validate that at least one search criteria is provided
    if not summary and not start_date and not end_date and not attendees:
        return "❌ Erro: É necessário fornecer pelo menos um critério de busca (título, data ou participantes)."

    try:
        # Get credentials and build service
        creds = get_calendar_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Search for events in Google Calendar
        event_result = service.events().list(
            calendarId="primary",
            timeMin=start_date,
            timeMax=end_date,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = event_result.get("items", [])

        if not events:
            return "❌ Nenhum evento encontrado no período especificado."

        # Filter events based on criteria
        target_event = None

        # Search by title (summary)
        if summary:
            events = [event for event in events if summary.lower() in event.get("summary", "").lower()]
            if not events:
                print(f"❌ Nenhum evento encontrado com o título '{summary}'.")
                return f"❌ Nenhum evento encontrado com o título '{summary}'."

        # Filter by attendee if provided
        if attendees:
            filtered_events = []
            for event in events:
                event_attendees = event.get("attendees", [])
                event_emails = [attendee.get("email", "") for attendee in event_attendees]
                if attendees in event_emails:
                    filtered_events.append(event)
            events = filtered_events
            
            if not events:
                return f"❌ Nenhum evento encontrado com o participante '{attendees}'."

        if len(events) > 1:
            return f"❌ Múltiplos eventos encontrados ({len(events)}). Seja mais específico nos critérios de busca."

        if len(events) == 0:
            return "❌ Nenhum evento encontrado com os critérios especificados."

        # Get the event to delete
        target_event = events[0]

        # Delete the event
        service.events().delete(calendarId="primary", eventId=target_event["id"]).execute()

        return f"✅ Evento '{target_event.get('summary', 'Sem título')}' excluído com sucesso!"

    except HttpError as error:
        error_code = getattr(error, 'resp', {}).get('status', '')
        msg = error.resp.get('body', {}).get('error', {}).get('message', '')
        
        # Check for permission errors
        if error_code == '403' or 'forbidden' in msg.lower():
            return f"❌ Erro de permissão: Você não tem autorização para excluir o evento '{target_event.get('summary', 'Sem título')}'. Apenas o organizador pode excluir este evento."
        elif error_code == '404' or 'not found' in msg.lower():
            return f"❌ Evento não encontrado: O evento pode ter sido excluído por outra pessoa ou não existe mais."
        else:
            return f"❌ Erro ao excluir evento: {msg}"

def edit_calendar_event(
    summary: str = None,
    start_date: str = None,
    end_date: str = None,
    attendees: str = None,
    new_summary: str = None,
    new_location: str = None,
    new_description: str = None,
    new_start: str = None,
    new_end: str = None,
    new_attendees: str = None
):
    """
    Edit an existing event in the user's calendar.

    Args:
        # Search criteria
        summary (str): Current event title to search for.
        start_date (str): Start date to filter events.
        end_date (str): End date to filter events.
        attendees (str): Attendee email to search for.
        
        # New values
        new_summary (str): New event title.
        new_location (str): New event location.
        new_description (str): New event description.
        new_start (str): New start date and time.
        new_end (str): New end date and time.
        new_attendees (str): New attendees (comma-separated emails).

    Returns:
        str: Success or error message.
    """

    print("Function called: edit_calendar_event")

    # Validate that at least one search criteria is provided
    if not summary and not start_date and not end_date and not attendees:
        return "❌ Erro: É necessário fornecer pelo menos um critério de busca (título, data ou participantes)."

    try:
        # Get credentials and build service
        creds = get_calendar_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Set search parameters
        if start_date is None:
            search_start = dt.datetime.now().isoformat()
        else:
            search_start = start_date

        if end_date is None:
            search_end = dt.datetime.fromisoformat(search_start) + dt.timedelta(days=30)
            search_end = search_end.isoformat()
        else:
            search_end = end_date

        # Search for events in Google Calendar
        event_result = service.events().list(
            calendarId="primary",
            timeMin=search_start,
            timeMax=search_end,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = event_result.get("items", [])

        if not events:
            return "❌ Nenhum evento encontrado no período especificado."

        # Filter by summary if provided
        if summary:
            events = [event for event in events if summary.lower() in event.get("summary", "").lower()]
            if not events:
                return f"❌ Nenhum evento encontrado com o título '{summary}'."

        # Filter by attendee if provided
        if attendees:
            filtered_events = []
            for event in events:
                event_attendees = event.get("attendees", [])
                event_emails = [attendee.get("email", "") for attendee in event_attendees]
                if attendees in event_emails:
                    filtered_events.append(event)
            events = filtered_events
            
            if not events:
                return f"❌ Nenhum evento encontrado com o participante '{attendees}'."

        if len(events) > 1:
            return f"❌ Múltiplos eventos encontrados ({len(events)}). Seja mais específico nos critérios de busca."

        if len(events) == 0:
            return "❌ Nenhum evento encontrado com os critérios especificados."

        # Get the event to edit
        target_event = events[0]

        # Update only the fields that were provided
        if new_summary:
            target_event["summary"] = new_summary
        
        if new_location:
            target_event["location"] = new_location
        
        if new_description:
            target_event["description"] = new_description
        
        if new_start:
            target_event["start"] = {
                "dateTime": new_start,
                "timeZone": "America/Sao_Paulo"
            }
        
        if new_end:
            target_event["end"] = {
                "dateTime": new_end,
                "timeZone": "America/Sao_Paulo"
            }
        
        if new_attendees:
            target_event["attendees"] = [{"email": new_attendees}]

        # Update the event
        updated_event = service.events().update(
            calendarId="primary",
            eventId=target_event["id"],
            body=target_event
        ).execute()

        return f"✅ Evento '{target_event.get('summary', 'Sem título')}' editado com sucesso!"

    except HttpError as error:
        if error.resp.status == 403:
            return f"❌ Erro de permissão: Você não tem autorização para editar este evento."
        elif error.resp.status == 410:
            return f"❌ Evento não encontrado: O evento pode ter sido excluído."
        else:
            msg = str(error)
            return f"❌ Erro ao editar evento: {msg}"

