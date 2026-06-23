import pandas as pd


POINTS = {
    "individual_scorer": 3,
    "goal_difference": 3,
    "total_goals": 4,
    "correct_outcome": 5,
    "correct_score": 10,
    "correct_score_all_scorers_bonus": 20,
    "correct_period": 5,
    "qualified_team": 5,
    "golden_boot": 15,
    "golden_ball": 15,
    "golden_glove": 15,
    "young_player": 15,
    "tournament_winner": 25,
}


def normalise_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def to_int(value, default: int = 0) -> int:
    try:
        if value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def is_true(value) -> bool:
    return normalise_text(value) in {"true", "1", "yes", "y"}


def outcome(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "home"
    if home_score < away_score:
        return "away"
    return "draw"


def same_id(series: pd.Series, value) -> pd.Series:
    return series.astype(str) == str(value)


def get_contestant_name(contestants: pd.DataFrame, contestant_id) -> str:
    row = contestants[same_id(contestants["contestant_id"], contestant_id)]
    if row.empty:
        return f"Contestant {contestant_id}"
    return str(row.iloc[0]["contestant_name"])


def score_scorers(
    match_id,
    contestant_id,
    predicted_scorers: pd.DataFrame,
    actual_scorers: pd.DataFrame,
    actual_total_goals: int,
) -> tuple[int, int, int]:
    if predicted_scorers.empty:
        preds = pd.DataFrame(columns=["match_id", "contestant_id", "team", "scorer_name", "is_own_goal"])
    else:
        preds = predicted_scorers[
            same_id(predicted_scorers["match_id"], match_id)
            & same_id(predicted_scorers["contestant_id"], contestant_id)
        ].copy()

    if actual_scorers.empty:
        actuals = pd.DataFrame(columns=["match_id", "team", "scorer_name", "is_own_goal"])
    else:
        actuals = actual_scorers[same_id(actual_scorers["match_id"], match_id)].copy()

    matched_actual_indexes = set()
    correct_scorers = 0

    for _, pred in preds.iterrows():
        pred_team = normalise_text(pred.get("team", ""))
        pred_name = normalise_text(pred.get("scorer_name", ""))
        pred_own_goal = is_true(pred.get("is_own_goal", ""))

        for actual_index, actual in actuals.iterrows():
            if actual_index in matched_actual_indexes:
                continue

            actual_team = normalise_text(actual.get("team", ""))
            actual_name = normalise_text(actual.get("scorer_name", ""))
            actual_own_goal = is_true(actual.get("is_own_goal", ""))

            if pred_team != actual_team:
                continue

            # Own goal rule:
            # Enter team as the team credited with the goal.
            # If own goal is predicted, the player name does not matter.
            if pred_own_goal and actual_own_goal:
                matched_actual_indexes.add(actual_index)
                correct_scorers += 1
                break

            if not pred_own_goal and not actual_own_goal and pred_name == actual_name:
                matched_actual_indexes.add(actual_index)
                correct_scorers += 1
                break

    scorer_points = correct_scorers * POINTS["individual_scorer"]

    actual_goals_entered = len(actuals)
    predicted_scorers_entered = len(preds)

    all_scorers_correct = (
        actual_goals_entered == actual_total_goals
        and predicted_scorers_entered == actual_total_goals
        and correct_scorers == actual_total_goals
    )

    return scorer_points, correct_scorers, int(all_scorers_correct)


def has_score_prediction(pred_row) -> bool:
    if pred_row is None:
        return False

    home_value = str(pred_row.get("pred_home_score", "")).strip()
    away_value = str(pred_row.get("pred_away_score", "")).strip()

    return home_value != "" and away_value != ""


def calculate_match_points(
    contestants: pd.DataFrame,
    matches: pd.DataFrame,
    predictions: pd.DataFrame,
    predicted_scorers: pd.DataFrame,
    results: pd.DataFrame,
    actual_scorers: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    if matches.empty or results.empty or contestants.empty:
        return pd.DataFrame(rows)

    completed_results = results[
        (results["home_score"].astype(str) != "")
        & (results["away_score"].astype(str) != "")
    ]

    if completed_results.empty:
        return pd.DataFrame(rows)

    for _, result in completed_results.iterrows():
        match_id = result["match_id"]

        match_rows = matches[same_id(matches["match_id"], match_id)]
        if match_rows.empty:
            continue

        match = match_rows.iloc[0]

        actual_home = to_int(result.get("home_score", ""))
        actual_away = to_int(result.get("away_score", ""))
        actual_total_goals = actual_home + actual_away
        actual_goal_difference = actual_home - actual_away
        actual_score_outcome = outcome(actual_home, actual_away)

        home_team = str(match["home_team"])
        away_team = str(match["away_team"])
        actual_result_text = f"{home_team} {actual_home}-{actual_away} {away_team}"

        for _, contestant in contestants.iterrows():
            contestant_id = contestant["contestant_id"]
            contestant_name = str(contestant["contestant_name"])

            pred = None

            if not predictions.empty:
                pred_rows = predictions[
                    same_id(predictions["match_id"], match_id)
                    & same_id(predictions["contestant_id"], contestant_id)
                ]

                if not pred_rows.empty:
                    pred = pred_rows.iloc[0]

            has_prediction = has_score_prediction(pred)

            # Default values for missing or blank predictions
            prediction_text = ""
            pred_winner = ""
            correct_scorers = 0
            scorer_points = 0
            goal_difference_points = 0
            total_goals_points = 0
            outcome_points = 0
            correct_score_points = 0
            all_scorers_bonus_points = 0
            period_points = 0
            raw_match_points = 0

            if has_prediction:
                pred_home = to_int(pred.get("pred_home_score", ""))
                pred_away = to_int(pred.get("pred_away_score", ""))

                prediction_text = f"{home_team} {pred_home}-{pred_away} {away_team}"
                pred_winner = pred.get("pred_winner", "")

                pred_total_goals = pred_home + pred_away
                pred_goal_difference = pred_home - pred_away
                pred_score_outcome = outcome(pred_home, pred_away)

                normalised_pred_winner = normalise_text(pred.get("pred_winner", ""))
                actual_winner = normalise_text(result.get("actual_winner", ""))

                if is_true(match.get("is_knockout", "")) and normalised_pred_winner and actual_winner:
                    correct_outcome = normalised_pred_winner == actual_winner
                else:
                    correct_outcome = pred_score_outcome == actual_score_outcome

                correct_score_points = (
                    POINTS["correct_score"]
                    if pred_home == actual_home and pred_away == actual_away
                    else 0
                )

                outcome_points = POINTS["correct_outcome"] if correct_outcome else 0

                total_goals_points = (
                    POINTS["total_goals"]
                    if pred_total_goals == actual_total_goals
                    else 0
                )

                goal_difference_points = (
                    POINTS["goal_difference"]
                    if pred_goal_difference == actual_goal_difference
                    else 0
                )

                scorer_points, correct_scorers, all_scorers_correct = score_scorers(
                    match_id,
                    contestant_id,
                    predicted_scorers,
                    actual_scorers,
                    actual_total_goals,
                )

                all_scorers_bonus_points = (
                    POINTS["correct_score_all_scorers_bonus"]
                    if correct_score_points > 0 and all_scorers_correct
                    else 0
                )

                if is_true(match.get("is_knockout", "")):
                    pred_period = normalise_text(pred.get("pred_period", ""))
                    actual_period = normalise_text(result.get("actual_period", ""))
                    if pred_period and pred_period == actual_period:
                        period_points = POINTS["correct_period"]

                raw_match_points = (
                    scorer_points
                    + goal_difference_points
                    + total_goals_points
                    + outcome_points
                    + correct_score_points
                    + all_scorers_bonus_points
                    + period_points
                )

            final_multiplier = 2 if is_true(match.get("is_final", "")) else 1
            total_match_points = raw_match_points * final_multiplier

            rows.append(
                {
                    "match_id": to_int(match_id),
                    "stage": match.get("stage", ""),
                    "home_team": home_team,
                    "away_team": away_team,
                    "contestant_id": to_int(contestant_id),
                    "contestant_name": contestant_name,
                    "prediction": prediction_text,
                    "pred_winner": pred_winner,
                    "actual_result": actual_result_text,
                    "actual_winner": result.get("actual_winner", ""),
                    "correct_scorers": correct_scorers,
                    "scorer_points": scorer_points,
                    "goal_difference_points": goal_difference_points,
                    "total_goals_points": total_goals_points,
                    "outcome_points": outcome_points,
                    "correct_score_points": correct_score_points,
                    "all_scorers_bonus_points": all_scorers_bonus_points,
                    "period_points": period_points,
                    "final_multiplier": final_multiplier,
                    "total_match_points": total_match_points,
                }
            )

    return pd.DataFrame(rows)

def calculate_group_points(
    contestants: pd.DataFrame,
    group_predictions: pd.DataFrame,
    group_results: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    if group_predictions.empty or group_results.empty:
        for _, contestant in contestants.iterrows():
            rows.append({"contestant_id": to_int(contestant["contestant_id"]), "group_points": 0})
        return pd.DataFrame(rows)

    actual_qualified = set(group_results["team"].map(normalise_text))

    for _, contestant in contestants.iterrows():
        contestant_id = contestant["contestant_id"]
        preds = group_predictions[same_id(group_predictions["contestant_id"], contestant_id)]
        correct = preds["team"].map(normalise_text).isin(actual_qualified).sum()
        rows.append(
            {
                "contestant_id": to_int(contestant_id),
                "group_points": int(correct) * POINTS["qualified_team"],
            }
        )

    return pd.DataFrame(rows)


def calculate_award_points(
    contestants: pd.DataFrame,
    award_predictions: pd.DataFrame,
    award_results: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    if award_predictions.empty or award_results.empty:
        for _, contestant in contestants.iterrows():
            rows.append(
                {
                    "contestant_id": to_int(contestant["contestant_id"]),
                    "award_points": 0,
                    "tournament_winner_points": 0,
                }
            )
        return pd.DataFrame(rows)

    actual = award_results.iloc[0].to_dict()

    for _, contestant in contestants.iterrows():
        contestant_id = contestant["contestant_id"]
        pred_rows = award_predictions[same_id(award_predictions["contestant_id"], contestant_id)]

        if pred_rows.empty:
            rows.append(
                {
                    "contestant_id": to_int(contestant_id),
                    "award_points": 0,
                    "tournament_winner_points": 0,
                }
            )
            continue

        pred = pred_rows.iloc[0].to_dict()

        def award_score(column_name: str, points: int) -> int:
            predicted = normalise_text(pred.get(column_name, ""))
            real = normalise_text(actual.get(column_name, ""))
            if predicted and real and predicted == real:
                return points
            return 0

        golden_boot_points = award_score("golden_boot", POINTS["golden_boot"])
        golden_ball_points = award_score("golden_ball", POINTS["golden_ball"])
        golden_glove_points = award_score("golden_glove", POINTS["golden_glove"])
        young_player_points = award_score("young_player", POINTS["young_player"])
        tournament_winner_points = award_score("tournament_winner", POINTS["tournament_winner"])

        rows.append(
            {
                "contestant_id": to_int(contestant_id),
                "award_points": golden_boot_points
                + golden_ball_points
                + golden_glove_points
                + young_player_points,
                "tournament_winner_points": tournament_winner_points,
            }
        )

    return pd.DataFrame(rows)


def calculate_leaderboard(
    contestants: pd.DataFrame,
    matches: pd.DataFrame,
    predictions: pd.DataFrame,
    predicted_scorers: pd.DataFrame,
    results: pd.DataFrame,
    actual_scorers: pd.DataFrame,
    group_predictions: pd.DataFrame,
    group_results: pd.DataFrame,
    award_predictions: pd.DataFrame,
    award_results: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    match_points = calculate_match_points(
        contestants,
        matches,
        predictions,
        predicted_scorers,
        results,
        actual_scorers,
    )

    if match_points.empty:
        match_totals = pd.DataFrame(
            {
                "contestant_id": contestants["contestant_id"].map(to_int),
                "match_points": 0,
            }
        )
    else:
        match_totals = (
            match_points.groupby("contestant_id", as_index=False)["total_match_points"]
            .sum()
            .rename(columns={"total_match_points": "match_points"})
        )

    group_points = calculate_group_points(contestants, group_predictions, group_results)
    award_points = calculate_award_points(contestants, award_predictions, award_results)

    leaderboard = contestants.copy()
    leaderboard["contestant_id"] = leaderboard["contestant_id"].map(to_int)

    leaderboard = leaderboard.merge(match_totals, on="contestant_id", how="left")
    leaderboard = leaderboard.merge(group_points, on="contestant_id", how="left")
    leaderboard = leaderboard.merge(award_points, on="contestant_id", how="left")

    for col in [
        "match_points",
        "group_points",
        "award_points",
        "tournament_winner_points",
    ]:
        leaderboard[col] = leaderboard[col].fillna(0).astype(int)

    leaderboard["total_points"] = (
        leaderboard["match_points"]
        + leaderboard["group_points"]
        + leaderboard["award_points"]
        + leaderboard["tournament_winner_points"]
    )

    leaderboard = leaderboard.sort_values(
        ["total_points", "match_points", "contestant_name"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    leaderboard.insert(0, "rank", leaderboard.index + 1)

    return leaderboard, match_points
