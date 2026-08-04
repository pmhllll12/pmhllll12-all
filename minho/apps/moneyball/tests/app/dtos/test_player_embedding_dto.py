from __future__ import annotations

from moneyball.app.dtos.player_embedding_dto import PlayerProfile


def _full_profile() -> PlayerProfile:
    return PlayerProfile(
        player_id="2012178",
        player_name="손흥민",
        e_player_name="Son Heung-min",
        nickname="손세이셔널",
        position="FW",
        back_no=7,
        nation="대한민국",
        height=183,
        weight=78,
        join_yyyy="2015",
        team_name="FC서울",
    )


def test_embedding_text_includes_every_present_field():
    text = _full_profile().to_embedding_text()

    assert text == (
        "이름 손흥민 (Son Heung-min), 닉네임 손세이셔널, 포지션 FW, 등번호 7, "
        "국적 대한민국, 키 183cm, 체중 78kg, 입단 2015, 소속팀 FC서울"
    )


def test_embedding_text_omits_missing_fields():
    profile = PlayerProfile(player_id="2012178", player_name="손흥민", position="FW")

    assert profile.to_embedding_text() == "이름 손흥민, 포지션 FW"


def test_embedding_text_uses_english_name_alone_when_korean_name_missing():
    profile = PlayerProfile(player_id="2012178", e_player_name="Son Heung-min")

    assert profile.to_embedding_text() == "이름 Son Heung-min"


def test_embedding_text_is_empty_when_both_names_missing():
    # 이름이 없으면 유사도 검색에서 선수를 식별할 수 없어 임베딩 대상에서 제외한다.
    profile = PlayerProfile(player_id="2012178", position="FW", back_no=7, team_name="FC서울")

    assert profile.to_embedding_text() == ""


def test_embedding_text_treats_blank_names_as_missing():
    profile = PlayerProfile(player_id="2012178", player_name="  ", e_player_name="", position="FW")

    assert profile.to_embedding_text() == ""
