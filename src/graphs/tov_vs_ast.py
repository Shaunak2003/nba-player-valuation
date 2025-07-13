import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.express as px

def tov_ast_graph(filtered_df, full_df, highlight_df):
    fig = px.scatter(
        filtered_df,
        x="AST",
        y="TOV",
        hover_name="Player",
        hover_data=["Team", "Pos", "Total_MP", "Possession_Control"],
        title="Turnovers vs Assists (Interactive)"
    )
    fig.update_traces(marker=dict(size=10, opacity=0.7))

    X = full_df[["AST"]]
    y = full_df["TOV"]
    reg = LinearRegression()
    reg.fit(X, y)
    x_range = np.linspace(X["AST"].min(), X["AST"].max(), 100)
    y_pred = reg.predict(x_range.reshape(-1, 1))

    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode='lines',
        name="Regression Line (All Players)",
        line=dict(color='red', dash='dash')
    ))

    if not highlight_df.empty:
        fig.add_trace(go.Scatter(
            x=highlight_df["AST"],
            y=highlight_df["TOV"],
            mode="markers+text",
            text=highlight_df["Player"],
            name="Selected Player",
            marker=dict(color="red", size=14, symbol="star"),
            textposition="top center"
        ))

    fig.update_layout(height=600)
    return fig
