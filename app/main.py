from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.database import SessionDep, engine
from app.models import (
    Hero, HeroCreate, HeroPublic, HeroUpdate,
    Mission, MissionCreate, MissionPublic, MissionUpdate,
    Team, TeamCreate, TeamPublic, TeamUpdate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Hero API - Lab 09", lifespan=lifespan)


@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    if (
        hero_in.team_id is not None
        and session.get(Team, hero_in.team_id) is None
    ):
        raise HTTPException(404, "Team not found")
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None,
):
    statement = select(Hero)
    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)
    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)
    if name is not None:
        statement = statement.where(Hero.name.ilike(f"%{name}%"))
    statement = statement.order_by(Hero.id).offset(offset).limit(limit)
    return session.exec(statement).all()


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(404, "Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(404, "Hero not found")
    data = hero_in.model_dump(exclude_unset=True)
    if (
        data.get("team_id") is not None
        and session.get(Team, data["team_id"]) is None
    ):
        raise HTTPException(404, "Team not found")
    if any(
        field in data and data[field] is None
        for field in ("name", "secret_name")
    ):
        raise HTTPException(422, "name and secret_name cannot be null")
    hero.sqlmodel_update(data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(404, "Hero not found")
    session.delete(hero)
    session.commit()
    return Response(status_code=204)


@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Team name already exists")
    session.refresh(team)
    return team


@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    return session.exec(select(Team).order_by(Team.id)).all()


@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def list_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(404, "Team not found")
    return team.heroes


@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    if hero is None or mission is None:
        raise HTTPException(404, "Hero or mission not found")
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return Response(status_code=204)


@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def list_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(404, "Hero not found")
    return hero.missions


# Part 10: complete CRUD for teams and missions.
@app.get("/teams/{team_id}", response_model=TeamPublic)
def get_team(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(404, "Team not found")
    return team


@app.patch("/teams/{team_id}", response_model=TeamPublic)
def update_team(team_id: int, team_in: TeamUpdate, session: SessionDep):
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(404, "Team not found")
    data = team_in.model_dump(exclude_unset=True)
    if any(value is None for value in data.values()):
        raise HTTPException(422, "Team fields cannot be null")
    team.sqlmodel_update(data)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Team name already exists")
    session.refresh(team)
    return team


@app.delete("/teams/{team_id}", status_code=204)
def delete_team(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(404, "Team not found")
    if team.heroes:
        raise HTTPException(409, "Team still has heroes")
    session.delete(team)
    session.commit()
    return Response(status_code=204)


@app.get("/missions", response_model=list[MissionPublic])
def list_missions(session: SessionDep):
    return session.exec(select(Mission).order_by(Mission.id)).all()


@app.get("/missions/{mission_id}", response_model=MissionPublic)
def get_mission(mission_id: int, session: SessionDep):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(404, "Mission not found")
    return mission


@app.patch("/missions/{mission_id}", response_model=MissionPublic)
def update_mission(mission_id: int, mission_in: MissionUpdate, session: SessionDep):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(404, "Mission not found")
    data = mission_in.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is None:
        raise HTTPException(422, "title cannot be null")
    mission.sqlmodel_update(data)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@app.delete("/missions/{mission_id}", status_code=204)
def delete_mission(mission_id: int, session: SessionDep):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(404, "Mission not found")
    session.delete(mission)
    session.commit()
    return Response(status_code=204)
