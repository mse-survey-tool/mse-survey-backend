import os

from fastapi import FastAPI, Path
from enum import Enum 
from starlette.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

from . import credentials
from . import survey


MDBCSTR = credentials.MDB_CONNECTION_STRING
FURL = credentials.FRONTEND_URL
BURL = credentials.BACKEND_URL


# create fastapi app
app = FastAPI()

# connect to mongodb via motor
client = AsyncIOMotorClient(MDBCSTR)
db = client['survey_database']

# list all the surveys here
surveys = [
    survey.SingleChoiceSurvey(
        identifier='test-survey',
        description='This survey tests the functionality of the backend',
        database=db,
        choices=['A', 'B', 'C'],
    )
]
surveys = {s.id: s for s in surveys}
SurveyName = Enum('SurveyName', {k: k for k in surveys.keys()}, type=str)


@app.get('/')
async def status():
    """Verify if database and mailing services are operational"""
    try:
        await client.server_info()
        # TODO add test for sending emails
    except:
        return {'status': 'database error'}
    else:
        return {'status': 'all services operational'}


@app.post('/{survey}/submit')
async def submit(
        survey: SurveyName = Path(
            ...,
            description='The identification tag of the survey',
        ),
    ):
    """Validate submission and store it under unverified submissions"""
    # TODO
    # return surveys[survey].submit()
    pass


@app.get('/{survey}/verify/{token}')
async def verify(
        survey: SurveyName = Path(
            ...,
            description='The identification tag of the survey',
        ),
        token: str = Path(
            ...,
            description='The verification token',
        ),
    ):
    """Verify user token and either fail or redirect to success page"""
    # TODO check if verfication was successful or not and page accordingly?
    surveys[survey].verify(token)
    return RedirectResponse(f'{FURL}/{survey}/success')


@app.get('/{survey}/results')
async def results(
        survey: SurveyName = Path(
            ...,
            description='The identification tag of the survey',
        ),
    ):
    """Fetch the results of the given survey"""
    return surveys[survey].results()