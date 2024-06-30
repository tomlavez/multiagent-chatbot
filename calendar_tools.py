import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type, Optional

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def getCalendarEvents(numEvents=5, start_date=None, end_date=None):
    # Credentials
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build(
            "calendar",
            "v3",
            credentials=creds,
        )

        if start_date is None:
            start_date = dt.datetime.now().isoformat()

        if end_date is None:
            end_date = dt.datetime.fromisoformat(start_date) + dt.timedelta(days=30)
            end_date = end_date.isoformat()
        else:
            end_date = dt.datetime.fromisoformat(end_date) + dt.timedelta(minutes=5)
            end_date = end_date.isoformat()

        event_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_date + "-03:00",
                timeMax=end_date + "-03:00",
                maxResults=numEvents,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = event_result.get("items", [])
        event_list = []

        for event in events:
            formatted_event = {
                "summary": event["summary"],
                "description": event["description"],
                "location": event["location"],
                "start": event["start"],
                "end": event["end"],
            }
            event_list.append(formatted_event)

        return event_list

    # Handle errors
    except HttpError as error:
        print(f"An error occurred: {error}")


class CalendarEventSearchInput(BaseModel):
    """Inputs for get_calendar_events"""

    numEvents: Optional[int] = Field(
        description="Numero de eventos a serem retornados. O padrão é 5."
    )
    start_date: Optional[str] = Field(
        description="Data a partir da qual os eventos serão procurados. A data deve estar no formato RFC 3339, por exemplo, 2024-06-30T13:31:47, . Se não fornecido, o padrão será o horário atual"
    )
    end_date: Optional[str] = Field(
        description="Data até a qual os eventos serão procurados. A data deve estar no formato RFC 3339, por exemplo, 2024-06-30T13:31:47. Se não fornecido, o padrão será trinta dias após a data de início."
    )


class GetCalendarEventsTool(BaseTool):
    name = "get_calendar_events"
    description = """
    Ferramenta para buscar eventos no calendário do Google. É possível passar o número de eventos a serem retornados e o horário a partir do qual os eventos serão retornados. O padrão é 5 eventos, o horário atual e trinta dias após o horário atual, respectivamente.
    """
    args_schema: Type[BaseModel] = CalendarEventSearchInput

    def _run(self, numEvents: int, start_date: str, end_date: str):
        events_response = getCalendarEvents(numEvents, start_date, end_date)
        return events_response


def createCalendarEvent(
    summary,
    location=None,
    description=None,
    start=None,
    end=None,
    attendees=[],
):

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

    # Check for conflicts
    conflito = getCalendarEvents(start_date=start, end_date=end)
    if conflito:
        return "Conflito de horário!"

    # Format attendees
    convidados = []
    for attendee in attendees:
        convidados.append({"email": attendee})

    # Credentials
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
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

        res = "Evento criado!"
        return res

    # Handle errors
    except HttpError as error:
        print(f"An error occurred: {error}")


class CalendarCreateInput(BaseModel):
    """Inputs para create_calendar_event"""

    summary: str = Field(description="Titulo do evento")
    location: Optional[str] = Field(
        description="Localização do evento. Caso nenhuma localização seja passada, coloque 'Não informado'."
    )
    description: Optional[str] = Field(
        description="Descrição do evento. Caso nenhuma descrição seja passada, faça uma descrição curta com base no titulo."
    )
    start: str = Field(
        description="Horário de início do evento a ser criado. Deve estar no formato RFC 3339, por exemplo, 2024-06-30T13:31:47."
    )
    end: Optional[str] = Field(
        description="Horário de término do evento a ser criado. Deve estar no formato RFC 3339, por exemplo, 2024-06-30T13:31:47."
    )
    attendees: Optional[list] = Field(
        description="Lista dos email dos participantes ['email@gmail.com', 'segundoemail@gmail.com']"
    )


class CreateCalendarEventTool(BaseTool):
    name = "create_calendar_event"
    description = """
    Ferramenta para criar um evento no calendário do Google. É necessário passar o título, a localização, a descrição e o horário de início. O horário de término e a lista de participante são opcionais. Caso o primeiro não seja passado, o evento terá duração de 30 minutos. Caso o segundo não seja passado, o evento não terá convidados adicionais.
    """
    args_schema: Type[BaseModel] = CalendarCreateInput

    def _run(
        self,
        summary: str,
        location: str,
        description: str,
        start: str,
        end: str,
        attendees: list,
    ):
        events_response = createCalendarEvent(
            summary, location, description, start, end, attendees
        )
        return events_response


class CurrentTimeInput(BaseModel):
    """Inputs for getting the current time"""

    pass


class CurrentTimeTool(BaseTool):
    name = "get_current_time"
    description = """
    Útil quando você deseja obter a hora atual em um timestamp RFC3339 com offset de fuso horário obrigatório, por exemplo, 2024-06-30T13:31:47.
    """
    args_schema: Type[BaseModel] = CurrentTimeInput

    def _run(self):
        # Return the current time in a format google calendar api can understand
        return (dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),)


class TimeDeltaInput(BaseModel):
    """Inputs for getting time deltas"""

    delta_days: Optional[int] = Field(
        description="Número de dias a serem adicionados ao horário atual. Deve ser um número inteiro."
    )
    delta_hours: Optional[int] = Field(
        description="Número de horas a serem adicionados ao horário atual. Deve ser um número inteiro."
    )
    delta_minutes: Optional[int] = Field(
        description="Número de minutos a serem adicionados ao horário atual. Deve ser um número inteiro."
    )
    delta_seconds: Optional[int] = Field(
        description="Número de segundos a serem adicionados ao horário atual. Deve ser um número inteiro."
    )


class TimeDeltaTool(BaseTool):
    name = "get_future_time"
    description = "Útil quando você deseja obter um horário futuro em um timestamp no formato RFC3339, dado um delta de tempo como 1 dia, 2 horas, 3 minutos, 4 segundos."
    args_schema: Type[BaseModel] = TimeDeltaInput

    def _run(
        self,
        delta_days: int = 0,
        delta_hours: int = 0,
        delta_minutes: int = 0,
        delta_seconds: int = 0,
    ):
        # Return the current time in a format google calendar api can understand
        return (
            dt.utcnow()
            + dt.timedelta(
                days=delta_days,
                hours=delta_hours,
                minutes=delta_minutes,
                seconds=delta_seconds,
            )
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")


class SpecificTimeInput(BaseModel):
    """Inputs for setting a specific time"""

    year: int = Field(description="Ano do evento")
    month: int = Field(description="Mês do evento")
    day: int = Field(description="Dia do evento")
    hour: int = Field(description="Hora do evento")
    minute: int = Field(description="Minuto do evento")


class SpecificTimeTool(BaseTool):
    name = "set_specific_time"
    description = "Define um horário específico para um evento, por exemplo, quando você quer criar um evento às 15h no dia 3 de junho de 2024."
    args_schema: Type[BaseModel] = SpecificTimeInput

    def _run(self, year: int, month: int, day: int, hour: int, minute: int):
        specific_time = dt.datetime(year, month, day, hour, minute)
        return specific_time.strftime("%Y-%m-%dT%H:%M:%S")


if __name__ == "__main__":
    print(dt.datetime.now().isoformat())
    events = getCalendarEvents(
        start_date="2024-07-03T20:00:00", end_date="2024-07-03T20:30:00"
    )
    for event in events:
        print(event)
