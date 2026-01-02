from models.profile import Profile
from utils.constants import FULL_PROFILE_SAMPLE, PROFILE_ADD_INFO, RAVEN_PROFILE_ADD_INFO


async def get_main_template(profile: Profile, user_rank: str = "") -> str:
    return FULL_PROFILE_SAMPLE.format(
            nickname=profile.nickname,
            telegram_tag= "@" + profile.telegram_tag if profile.telegram_tag else "Нет",
            gender=profile.gender if profile.gender else "Нет",
            level=profile.experience // 100 + 1,
            polite=str(round(profile.polite, 1)) + "⭐" if profile.teammate_ids else "Нет оценок",
            skill=str(round(profile.skill, 1)) + "⭐" if profile.teammate_ids else "Нет оценок",
            team_game=str(round(profile.team_game, 1)) + "⭐" if profile.teammate_ids else "Нет оценок", 
            games=profile.games_str,
            rank=user_rank,
            add_info=PROFILE_ADD_INFO.format(time=", ".join(profile.convenient_time) if profile.convenient_time else "Не указано", 
                                             about=profile.about, goal=", ".join(profile.goals) if profile.goals else "Не указаны")
        )

async def get_warcraft_profile_template(profile: Profile) -> str:
    games = {game.name: game.rank for game in profile.games}

    if games.get("Warcraft", False):
        user_rank = f"\n<b>Ранг:</b>\n"
        subranks = []
        for subrank in games["Warcraft"].split(";")[:-1]:
            mode, info = subrank.split("/")
            subranks.append(f"- {mode}: {info}")
        user_rank += "\n".join(subranks)
    else:
        user_rank = f"\n<b>Ранг:</b> Не указан"

    return await get_main_template(profile, user_rank)


async def get_other_game_profile_template(profile: Profile, game: str) -> str:
    games = {game.name: game.rank for game in profile.games}

    if games.get(game, False):
        user_rank = f"\n<b>Ранг:</b> {games[game]}"
    else:
        user_rank = f"\n<b>Ранг:</b> Не указан"

    return await get_main_template(profile, user_rank)

async def get_raven_main_template(profile: Profile, user_rank: str = "", add_info: str = "") -> str:
    return FULL_PROFILE_SAMPLE.format(
            nickname=profile.nickname,
            telegram_tag= "@" + profile.telegram_tag if profile.telegram_tag else "Нет",
            gender=profile.gender if profile.gender else "Нет",
            level=profile.experience // 100 + 1,
            polite=str(round(profile.polite, 1)) + "⭐" if profile.teammate_ids else "Нет оценок",
            skill=str(round(profile.skill, 1)) + "⭐" if profile.teammate_ids else "Нет оценок",
            team_game=str(round(profile.team_game, 1)) + "⭐" if profile.teammate_ids else "Нет оценок", 
            games=profile.games_str,
            rank=user_rank,
            add_info=add_info
        )

async def get_raven2_profile_template(profile: Profile, game: str) -> str:
    games = {game.name: game.rank for game in profile.games}

    if games.get(game, False):
        parts = games[game].split("/")

        print(parts)

        if game == "Raven 2":
            server = f"{parts[0]} - {parts[1]}"
        else:
            server = parts[0]

        if game == "Lineage 2M":
            class_ = f"{parts[1]}-{parts[2]}"
        else:
            class_ = parts[2]

        level = parts[3]

        if parts[-2] == "Да":
            donate = f"{parts[-2]}, {parts[-1]}"
        else:
            donate = "Нет"


        add_info = RAVEN_PROFILE_ADD_INFO.format(
                                             server=server,
                                             class_=class_,
                                             level=level,
                                             time=", ".join(profile.convenient_time) if profile.convenient_time else "Не указано", 
                                             donate=donate,
                                             about=profile.about, 
                                             goal=", ".join(profile.goals) if profile.goals else "Не указаны")
        
        return await get_raven_main_template(profile, "", add_info)
    

async def get_profile_template(profile: Profile, game: str) -> str:
    if game == "Warcraft":
        profile_template = await get_warcraft_profile_template(profile)
    elif game in ("Raven 2", "Lineage 2M"):
        profile_template = await get_raven2_profile_template(profile, game)
    else:
        profile_template = await get_other_game_profile_template(profile, game)

    return profile_template

async def get_profile_template_no_rank(profile: Profile) -> str:
    return await get_main_template(profile)