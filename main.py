import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Statistical Plotting Tool",
    layout="centered"
)

st.title("Statistical Plotting Tool")

st.write(
    "Upload a CSV file containing two columns. "
    "The second column will be used for the statistical analysis."
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
    # Plot information
    # --------------------------------------------------

    st.subheader("Plot Information")

    axis_label = st.text_input(
        "Axis label (include the unit if applicable)",
        value=""
    )

    # ==================================================
    # SECTION 1 — BOX-AND-WHISKER PLOT
    # ==================================================

    st.header("Section 1: Box-and-Whisker Plot")

    st.info(
        "The whiskers extend from the minimum to the maximum value."
    )

    # Five-number summary

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

    # Box-and-whisker plot

    st.subheader("Box-and-Whisker Plot")

    fig1, ax1 = plt.subplots(figsize=(8, 3))

    ax1.boxplot(
        data,
        vert=False,
        whis=(0, 100),       # minimum to maximum
        showfliers=False,
        widths=0.45
    )

    ax1.set_xlabel(axis_label)
    ax1.set_yticks([])

    ax1.grid(
        True,
        axis="x",
        alpha=0.3
    )

    fig1.tight_layout()

    st.pyplot(fig1)

    # Download box plot

    buffer1 = BytesIO()

    fig1.savefig(
        buffer1,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    buffer1.seek(0)

    st.download_button(
        label="Download Box-and-Whisker Plot",
        data=buffer1,
        file_name="box_whisker_plot.png",
        mime="image/png"
    )

    plt.close(fig1)

    # ==================================================
    # SECTION 2 — HISTOGRAM
    # ==================================================

    st.header("Section 2: Histogram")

    # Number of observations
    n = len(data)

    # Calculate recommended number of bins
    if n < 50:
        k_raw = 1.87 * (n - 1) ** 0.40 + 1
    else:
        k_raw = np.sqrt(n)

    # Round to nearest whole number
    k_opt = max(1, int(round(k_raw)))

    # Data limits
    x_min = data.min()
    x_max = data.max()

    # Recommended bin size
    bin_size_opt = (x_max - x_min) / k_opt

    # --------------------------------------------------
    # Show recommended values
    # --------------------------------------------------

    st.subheader("Recommended Histogram Parameters")

    st.write(f"Number of data points: **{n}**")

    st.write(
        f"Recommended number of bins: **{k_opt}**"
    )

    st.write(
        f"Minimum data value: **{x_min:.4g}**"
    )

    st.write(
        f"Recommended bin size: **{bin_size_opt:.4g}**"
    )

    st.write(
        "Use these values as guidance when selecting the "
        "starting point and bin size for your histogram."
    )

    # --------------------------------------------------
    # Student input
    # --------------------------------------------------

    st.subheader("Choose Histogram Parameters")

    starting_x = st.number_input(
        "Starting x (lower bound of the first bin)",
        value=float(x_min)
    )

    bin_size = st.number_input(
        "Bin size",
        min_value=0.0,
        value=float(bin_size_opt)
    )

    # --------------------------------------------------
    # Histogram
    # --------------------------------------------------

    if bin_size > 0:

        # Make sure the selected starting point includes
        # the minimum observation
        if starting_x > x_min:

            st.warning(
                "The starting x is greater than the minimum "
                "data value. Some observations would not be "
                "included in the histogram."
            )

        else:

            # Determine how many bins are required to include xmax
            number_of_bins = int(
                np.ceil((x_max - starting_x) / bin_size)
            )

            # At least one bin
            number_of_bins = max(1, number_of_bins)

            # Construct bin edges
            bin_edges = (
                starting_x
                + np.arange(number_of_bins + 1) * bin_size
            )

            # Protect against floating-point roundoff
            if bin_edges[-1] < x_max:
                bin_edges = np.append(
                    bin_edges,
                    bin_edges[-1] + bin_size
                )

            # ------------------------------------------
            # Plot histogram
            # ------------------------------------------

            st.subheader("Histogram")

            fig2, ax2 = plt.subplots(figsize=(8, 5))

            ax2.hist(
                data,
                bins=bin_edges,
                edgecolor="black"
            )

            ax2.set_xlabel(axis_label)
            ax2.set_ylabel("Frequency")

            ax2.grid(
                True,
                axis="y",
                alpha=0.3
            )

            fig2.tight_layout()

            st.pyplot(fig2)

            # ------------------------------------------
            # Show selected bin information
            # ------------------------------------------

            st.write(
                f"Your histogram uses **{len(bin_edges) - 1} bins** "
                f"with a bin size of **{bin_size:.4g}**."
            )

            # ------------------------------------------
            # Download histogram
            # ------------------------------------------

            buffer2 = BytesIO()

            fig2.savefig(
                buffer2,
                format="png",
                dpi=300,
                bbox_inches="tight"
            )

            buffer2.seek(0)

            st.download_button(
                label="Download Histogram",
                data=buffer2,
                file_name="histogram.png",
                mime="image/png"
            )

            plt.close(fig2)

    else:

        st.warning(
            "Please enter a bin size greater than zero."
        )
