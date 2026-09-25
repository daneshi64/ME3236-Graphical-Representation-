import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Box-and-Whisker Plot",
    layout="centered"
)

st.title("Box-and-Whisker Plot")

st.write(
    "Upload a CSV file containing two columns. "
    "The second column will be used to create the box-and-whisker plot."
)

st.info(
    "The whiskers extend from the minimum to the maximum value."
)

# --------------------------------------------------
# Upload CSV file
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    # Read CSV file
    df = pd.read_csv(uploaded_file)

    # Check number of columns
    if df.shape[1] < 2:
        st.error("The CSV file must contain at least two columns.")
        st.stop()

    # Use second column as measured data
    data = pd.to_numeric(df.iloc[:, 1], errors="coerce")

    # Remove missing or non-numeric values
    data = data.dropna()

    if len(data) == 0:
        st.error("No numeric data were found in the second column.")
        st.stop()

    # --------------------------------------------------
    # Show imported data
    # --------------------------------------------------

    st.subheader("Imported Data")

    st.dataframe(
        df,
        use_container_width=True
    )

    # --------------------------------------------------
    # Axis label
    # --------------------------------------------------

    st.subheader("Plot Information")

    axis_label = st.text_input(
        "Axis label (include the unit if applicable)",
        value=""
    )

    # --------------------------------------------------
    # Five-number summary
    # --------------------------------------------------

    minimum = data.min()
    q1 = data.quantile(0.25)
    median = data.median()
    q3 = data.quantile(0.75)
    maximum = data.max()

    st.subheader("Five-Number Summary")

    summary = pd.DataFrame({
        "Statistic": [
            "Minimum",
            "Q1",
            "Median",
            "Q3",
            "Maximum"
        ],
        "Value": [
            minimum,
            q1,
            median,
            q3,
            maximum
        ]
    })

    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # Horizontal box-and-whisker plot
    # --------------------------------------------------

    st.subheader("Box-and-Whisker Plot")

    fig, ax = plt.subplots(figsize=(8, 3))

    ax.boxplot(
        data,
        vert=False,          # horizontal box plot
        whis=(0, 100),       # whiskers = minimum to maximum
        showfliers=False,
        widths=0.45
    )

    # X-axis label
    ax.set_xlabel(axis_label)

    # Remove unnecessary y-axis category
    ax.set_yticks([])

    # Vertical grid lines
    ax.grid(
        True,
        axis="x",
        alpha=0.3
    )

    fig.tight_layout()

    st.pyplot(fig)

    # --------------------------------------------------
    # Download plot
    # --------------------------------------------------

    buffer = BytesIO()

    fig.savefig(
        buffer,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    buffer.seek(0)

    st.download_button(
        label="Download Plot",
        data=buffer,
        file_name="box_whisker_plot.png",
        mime="image/png"
    )

    plt.close(fig)
