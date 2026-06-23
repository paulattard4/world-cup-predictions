import pandas as pd
import streamlit as st

from data_loader import get_data_source_name, load_all_data
from scoring import POINTS, calculate_leaderboard


st.set_page_config(
    page_title="World Cup 2026 Predictions",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        :root {
            --wc-blue: #3158F4;
            --wc-green: #19C95B;
            --wc-lime: #B8F000;
            --wc-red: #E02009;
            --wc-dark: #111827;
            --wc-muted: #4B5563;
            --wc-bg: #F3F4F6;
            --wc-card: #FFFFFF;
            --wc-border: #D1D5DB;
        }

        /* Main app background */
        .stApp {
            background: var(--wc-bg) !important;
            color: var(--wc-dark) !important;
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        /* Default text: always dark */
        h1, h2, h3, h4, h5, h6,
        p, span, label, div {
            color: var(--wc-dark);
        }

        h1, h2, h3 {
            font-weight: 850;
            letter-spacing: -0.02em;
        }

        /* Hero: light card, dark text, colourful shapes */
        .hero-wrap {
            position: relative;
            overflow: hidden;
            border-radius: 30px;
            background: #FFFFFF;
            min-height: 220px;
            padding: 34px 36px;
            margin-bottom: 26px;
            border: 3px solid var(--wc-dark);
            box-shadow: 8px 8px 0 rgba(17, 24, 39, 0.14);
        }

        .hero-blue {
            position: absolute;
            left: -8%;
            top: -30%;
            width: 54%;
            height: 110%;
            background: var(--wc-blue);
            border-radius: 0 0 220px 0;
            opacity: 0.95;
            z-index: 0;
        }

        .hero-red {
            position: absolute;
            right: -6%;
            top: -8%;
            width: 36%;
            height: 46%;
            background: var(--wc-red);
            border-radius: 0 0 0 160px;
            z-index: 0;
        }

        .hero-green {
            position: absolute;
            right: -8%;
            bottom: -24%;
            width: 46%;
            height: 82%;
            background: var(--wc-green);
            border-radius: 200px 0 0 0;
            z-index: 0;
        }

        .hero-lime {
            position: absolute;
            left: 36%;
            top: 28%;
            width: 26%;
            height: 52%;
            background: var(--wc-lime);
            border-radius: 120px 120px 12px 120px;
            z-index: 0;
        }

        .hero-content {
            position: relative;
            z-index: 2;
            max-width: 720px;
            background: rgba(255,255,255,0.92);
            border-radius: 24px;
            padding: 22px 24px;
            border: 2px solid var(--wc-dark);
        }

        .hero-year {
            display: inline-block;
            background: var(--wc-lime);
            color: var(--wc-dark) !important;
            font-weight: 950;
            font-size: 40px;
            line-height: 1;
            padding: 12px 20px;
            border-radius: 20px;
            border: 3px solid var(--wc-dark);
            margin-bottom: 16px;
        }

        .hero-title {
            color: var(--wc-dark) !important;
            font-size: 38px;
            font-weight: 950;
            line-height: 1.05;
            margin: 0 0 8px 0;
            letter-spacing: -0.035em;
        }

        .hero-subtitle {
            color: var(--wc-muted) !important;
            font-size: 16px;
            font-weight: 650;
            max-width: 650px;
            margin: 0;
        }

        /* Sidebar only: dark background, white text */
        section[data-testid="stSidebar"] {
            background: #111827 !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div {
            color: #FFFFFF !important;
        }

        /* Buttons */
        .stButton > button {
            background: var(--wc-lime) !important;
            color: var(--wc-dark) !important;
            border: 2px solid var(--wc-dark) !important;
            border-radius: 999px !important;
            font-weight: 850 !important;
        }

        .stButton > button:hover {
            background: #D6FF34 !important;
            color: var(--wc-dark) !important;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            background: #FFFFFF !important;
            border-radius: 18px !important;
            padding: 16px !important;
            border: 2px solid var(--wc-border) !important;
            box-shadow: 0 4px 12px rgba(17,24,39,0.08) !important;
        }

        div[data-testid="stMetric"] * {
            color: var(--wc-dark) !important;
        }

        /* Tables */
        div[data-testid="stDataFrame"] {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 8px !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: 0 4px 12px rgba(17,24,39,0.06) !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            background: #FFFFFF !important;
            color: var(--wc-dark) !important;
            border-radius: 999px !important;
            border: 1px solid var(--wc-border) !important;
            font-weight: 800 !important;
        }

        button[data-baseweb="tab"] * {
            color: var(--wc-dark) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: var(--wc-lime) !important;
            color: var(--wc-dark) !important;
            border: 2px solid var(--wc-dark) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] * {
            color: var(--wc-dark) !important;
        }

        /* Selectbox: white background, dark text */
        div[data-baseweb="select"] > div {
            background: #FFFFFF !important;
            color: var(--wc-dark) !important;
            border: 1px solid var(--wc-border) !important;
            border-radius: 12px !important;
        }

        div[data-baseweb="select"] * {
            color: var(--wc-dark) !important;
        }

        /* Dropdown menu: white background, dark text */
        div[data-baseweb="popover"],
        div[role="listbox"] {
            background: #FFFFFF !important;
            color: var(--wc-dark) !important;
        }

        div[role="option"] {
            background: #FFFFFF !important;
            color: var(--wc-dark) !important;
        }

        div[role="option"] * {
            color: var(--wc-dark) !important;
        }

        div[role="option"]:hover {
            background: #EEF2FF !important;
            color: var(--wc-dark) !important;
        }

        /* Alerts */
        div[data-testid="stAlert"] {
            background: #FFFFFF !important;
            border-radius: 14px !important;
            border: 1px solid var(--wc-border) !important;
        }

        div[data-testid="stAlert"] * {
            color: var(--wc-dark) !important;
        }

        /* Expanders */
        details {
            background: #FFFFFF !important;
            border-radius: 14px !important;
            border: 1px solid var(--wc-border) !important;
        }

        details * {
            color: var(--wc-dark) !important;
        }

        @media (max-width: 768px) {
            .hero-wrap {
                padding: 22px;
            }

            .hero-content {
                padding: 18px;
            }

            .hero-title {
                font-size: 30px;
            }

            .hero-year {
                font-size: 32px;
            }
        }
        
        /* FINAL FIX: dropdown menu readability */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"],
        ul[role="listbox"],
        div[role="listbox"] {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 14px !important;
        }

        div[data-baseweb="popover"] *,
        div[data-baseweb="menu"] *,
        ul[role="listbox"] *,
        div[role="listbox"] * {
            color: #111827 !important;
            background-color: transparent !important;
        }

        li[role="option"],
        div[role="option"] {
            background: #FFFFFF !important;
            color: #111827 !important;
            min-height: 44px !important;
            padding: 10px 14px !important;
            font-size: 15px !important;
        }

        li[role="option"] *,
        div[role="option"] * {
            color: #111827 !important;
        }

        li[role="option"]:hover,
        div[role="option"]:hover,
        div[data-baseweb="popover"] div[aria-selected="true"],
        div[data-baseweb="menu"] div[aria-selected="true"] {
            background: #EEF2FF !important;
            color: #111827 !important;
        }

        li[role="option"]:hover *,
        div[role="option"]:hover *,
        div[data-baseweb="popover"] div[aria-selected="true"] *,
        div[data-baseweb="menu"] div[aria-selected="true"] * {
            color: #111827 !important;
        }

        /* Selected dropdown box */
        div[data-baseweb="select"] > div {
            background: #FFFFFF !important;
            color: #111827 !important;
            min-height: 46px !important;
            border: 2px solid #D1D5DB !important;
            border-radius: 14px !important;
        }

        div[data-baseweb="select"] * {
            color: #111827 !important;
        }

        div[data-baseweb="select"] svg {
            fill: #111827 !important;
        }

        /* Bigger, less tight tab buttons */
        div[data-baseweb="tab-list"] {
            gap: 10px !important;
            flex-wrap: wrap !important;
            padding: 8px 0 16px 0 !important;
        }

        button[data-baseweb="tab"] {
            min-height: 48px !important;
            padding: 12px 24px !important;
            border-radius: 999px !important;
            font-size: 16px !important;
            margin-right: 4px !important;
        }

        button[data-baseweb="tab"] p {
            font-size: 16px !important;
            font-weight: 850 !important;
        }

        
        /* FINAL FIX: very top Streamlit header */
        header[data-testid="stHeader"] {
            background: #FFFFFF !important;
            color: #111827 !important;
            box-shadow: 0 1px 0 rgba(17, 24, 39, 0.08) !important;
        }

        header[data-testid="stHeader"] * {
            color: #111827 !important;
            fill: #111827 !important;
        }

        /* Keep main hero/header card white with dark text */
        .hero-wrap {
            background: #FFFFFF !important;
        }

        .hero-content {
            background: rgba(255, 255, 255, 0.95) !important;
        }

        .hero-title,
        .hero-subtitle,
        .hero-content,
        .hero-content * {
            color: #111827 !important;
        }

        .hero-subtitle {
            color: #4B5563 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

def hero_section():
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-blue"></div>
            <div class="hero-red"></div>
            <div class="hero-green"></div>
            <div class="hero-lime"></div>
            <div class="hero-content">
                <div class="hero-year">2026</div>
                <div class="hero-title">World Cup Prediction Leaderboard</div>
                <div class="hero-subtitle">
                    Match predictions, scorer picks, group qualifiers, award picks, and full points breakdowns.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def style_total_match_points(df: pd.DataFrame):
    if "total_match_points" not in df.columns:
        return df

    return df.style.apply(
        lambda col: [
            "background-color: #B8F000; color: #111827; font-weight: 900;"
            if col.name == "total_match_points"
            else ""
            for _ in col
        ],
        axis=0,
    )

def same_value(series: pd.Series, value) -> pd.Series:
    return series.astype(str) == str(value)


def is_true(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def format_scorer_name(row: pd.Series) -> str:
    if is_true(row.get("is_own_goal", "")):
        return "own goal"
    return str(row.get("scorer_name", "")).strip()


def format_scorers_for_match(
    scorers_df: pd.DataFrame,
    match_id,
    contestant_id=None,
) -> str:
    if scorers_df.empty or "match_id" not in scorers_df.columns:
        return "No scorers"

    rows = scorers_df[same_value(scorers_df["match_id"], match_id)].copy()

    if contestant_id is not None and "contestant_id" in rows.columns:
        rows = rows[same_value(rows["contestant_id"], contestant_id)].copy()

    if rows.empty:
        return "No scorers"

    parts = []

    for team, team_rows in rows.groupby("team", sort=False):
        names = [format_scorer_name(row) for _, row in team_rows.iterrows()]
        names = [name for name in names if name]
        if names:
            parts.append(f"{team}: {', '.join(names)}")

    if not parts:
        return "No scorers"

    return " | ".join(parts)



inject_custom_css()

hero_section()


with st.expander("Controls", expanded=False):
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Data source: {get_data_source_name()}")
    st.caption("Edit Google Sheets, then refresh.")


data = load_all_data()

contestants = data["contestants"]
matches = data["matches"]
match_predictions = data["match_predictions"]
predicted_scorers = data["predicted_scorers"]
results = data["results"]
actual_scorers = data["actual_scorers"]
group_predictions = data["group_predictions"]
group_results = data["group_results"]
award_predictions = data["award_predictions"]
award_results = data["award_results"]


required_contestant_cols = {"contestant_id", "contestant_name"}
if contestants.empty or not required_contestant_cols.issubset(set(contestants.columns)):
    st.error("Missing contestants. Check the contestants tab in Google Sheets.")
    st.stop()


leaderboard, match_points = calculate_leaderboard(
    contestants=contestants,
    matches=matches,
    predictions=match_predictions,
    predicted_scorers=predicted_scorers,
    results=results,
    actual_scorers=actual_scorers,
    group_predictions=group_predictions,
    group_results=group_results,
    award_predictions=award_predictions,
    award_results=award_results,
)


top_cols = st.columns(4)

with top_cols[0]:
    st.metric("Contestants", len(contestants))

with top_cols[1]:
    st.metric("Matches entered", len(matches))

with top_cols[2]:
    completed_matches = 0 if results.empty else len(results[results["home_score"].astype(str) != ""])
    st.metric("Completed matches", completed_matches)

with top_cols[3]:
    if leaderboard.empty:
        st.metric("Leader", "-")
    else:
        leader = leaderboard.iloc[0]
        st.metric("Leader", f"{leader['contestant_name']} ({leader['total_points']})")


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Leaderboard",
        "Matches",
        "Contestants",
        "Groups",
        "Awards",
        "Rules",
    ]
)


with tab1:
    st.header("Leaderboard")

    st.dataframe(
        leaderboard[
            [
                "rank",
                "contestant_name",
                "match_points",
                "group_points",
                "award_points",
                "tournament_winner_points",
                "total_points",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


with tab2:
    st.header("Match-by-match scoring")

    if match_points.empty:
        st.info("No scored matches yet. Add rows to results and actual_scorers.")
    else:
        match_options = (
            match_points[["match_id", "home_team", "away_team"]]
            .drop_duplicates()
            .sort_values("match_id")
        )

        labels = {
            row["match_id"]: f"{row['match_id']} — {row['home_team']} vs {row['away_team']}"
            for _, row in match_options.iterrows()
        }

        selected_match = st.selectbox(
            "Select match",
            options=list(labels.keys()),
            format_func=lambda x: labels[x],
        )

        filtered = match_points[match_points["match_id"] == selected_match].copy()

        filtered["predicted_scorers"] = filtered.apply(
            lambda row: format_scorers_for_match(
                predicted_scorers,
                selected_match,
                row["contestant_id"],
            ),
            axis=1,
        )

        filtered = filtered.sort_values(
            "total_match_points",
            ascending=False,
        )

        actual_scorers_text = format_scorers_for_match(
            actual_scorers,
            selected_match,
        )

        actual_score_text = ""
        if not filtered.empty and "actual_result" in filtered.columns:
            actual_score_text = str(filtered["actual_result"].iloc[0]).strip()

        actual_score_and_scorers = actual_scorers_text
        if actual_score_text:
            actual_score_and_scorers = f"{actual_score_text}\n\n{actual_scorers_text}"

        st.subheader("Actual score and scorers")
        st.info(actual_score_and_scorers)

        st.subheader("Prediction and scoring breakdown")

        match_breakdown_display = filtered[
            [
                "contestant_name",
                "prediction",
                "predicted_scorers",
                "pred_winner",
                "actual_result",
                "actual_winner",
                "correct_scorers",
                "scorer_points",
                "goal_difference_points",
                "total_goals_points",
                "outcome_points",
                "correct_score_points",
                "all_scorers_bonus_points",
                "period_points",
                "final_multiplier",
                "total_match_points",
            ]
        ]

        st.dataframe(
            style_total_match_points(match_breakdown_display),
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("Raw actual scorer rows"):
            scorers = actual_scorers[
                actual_scorers["match_id"].astype(str) == str(selected_match)
            ] if not actual_scorers.empty else pd.DataFrame()

            if scorers.empty:
                st.info("No actual scorers entered for this match.")
            else:
                st.dataframe(scorers, use_container_width=True, hide_index=True)


with tab3:
    st.header("Contestant detail")

    selected_contestant = st.selectbox(
        "Select contestant",
        contestants["contestant_name"].tolist(),
    )

    selected_id = contestants[
        contestants["contestant_name"] == selected_contestant
    ]["contestant_id"].iloc[0]

    selected_leaderboard = leaderboard[
        leaderboard["contestant_id"].astype(str) == str(selected_id)
    ]

    st.subheader("Total summary")
    st.dataframe(
        selected_leaderboard[
            [
                "rank",
                "contestant_name",
                "match_points",
                "group_points",
                "award_points",
                "tournament_winner_points",
                "total_points",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Match breakdown")

    if match_points.empty:
        st.info("No completed match scores yet.")
    else:
        contestant_matches = match_points[
            match_points["contestant_id"].astype(str) == str(selected_id)
        ].copy().sort_values("match_id")

        contestant_matches["predicted_scorers"] = contestant_matches.apply(
            lambda row: format_scorers_for_match(
                predicted_scorers,
                row["match_id"],
                row["contestant_id"],
            ),
            axis=1,
        )

        contestant_matches["actual_scorers"] = contestant_matches.apply(
            lambda row: format_scorers_for_match(
                actual_scorers,
                row["match_id"],
            ),
            axis=1,
        )

        contestant_match_display = contestant_matches[
            [
                "match_id",
                "stage",
                "home_team",
                "away_team",
                "prediction",
                "predicted_scorers",
                "actual_result",
                "actual_scorers",
                "total_match_points",
                "scorer_points",
                "goal_difference_points",
                "total_goals_points",
                "outcome_points",
                "correct_score_points",
                "all_scorers_bonus_points",
                "period_points",
            ]
        ]

        st.dataframe(
            style_total_match_points(contestant_match_display),
            use_container_width=True,
            hide_index=True,
        )


with tab4:
    st.header("Group qualifier predictions")

    st.subheader("Predictions")
    if group_predictions.empty:
        st.info("No group qualifier predictions entered yet.")
    else:
        display = group_predictions.merge(contestants, on="contestant_id", how="left")
        st.dataframe(
            display[["contestant_name", "team"]],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Actual qualified teams")
    if group_results.empty:
        st.info("No group results entered yet.")
    else:
        st.dataframe(group_results, use_container_width=True, hide_index=True)


with tab5:
    st.header("Award and tournament winner predictions")

    st.subheader("Predictions")
    if award_predictions.empty:
        st.info("No award predictions entered yet.")
    else:
        display = award_predictions.merge(contestants, on="contestant_id", how="left")
        st.dataframe(
            display[
                [
                    "contestant_name",
                    "tournament_winner",
                    "golden_boot",
                    "golden_ball",
                    "golden_glove",
                    "young_player",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Actual winners")
    if award_results.empty:
        st.info("No actual award results entered yet.")
    else:
        st.dataframe(award_results, use_container_width=True, hide_index=True)


with tab6:
    st.header("Rules")

    st.markdown(
        f"""
### Match points

| Rule | Points |
|---|---:|
| Each individual scorer | {POINTS["individual_scorer"]} |
| Goal difference | {POINTS["goal_difference"]} |
| Total goals | {POINTS["total_goals"]} |
| Correct outcome | {POINTS["correct_outcome"]} |
| Correct score | {POINTS["correct_score"]} |
| Correct score + all correct scorers bonus | {POINTS["correct_score_all_scorers_bonus"]} |
| Knockout correct period: FT / ET / Pens | {POINTS["correct_period"]} |

### Tournament points

| Rule | Points |
|---|---:|
| Each qualified team | {POINTS["qualified_team"]} |
| Golden Boot winner | {POINTS["golden_boot"]} |
| Golden Ball winner | {POINTS["golden_ball"]} |
| Golden Glove winner | {POINTS["golden_glove"]} |
| Young Player Award winner | {POINTS["young_player"]} |
| Tournament winner | {POINTS["tournament_winner"]} |

### Special rules

- Every scoring line is independent, so points stack.
- The final counts double for match prediction points.
- Own goal predictions do not require the player name.
- For own goals, enter the team credited with the goal.
- For penalty shootouts, do not include penalty shootout goals in the score.
- For knockout matches, `pred_winner` and `actual_winner` are used for correct outcome.
- If the exact score is 0-0 and no scorers were predicted or scored, the all-scorers bonus can apply.
"""
    )
