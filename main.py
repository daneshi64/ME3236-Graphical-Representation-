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
    "The first column contains the index or location, and the second "
    "column contains the measured data."
)

# --------------------------------------------------
# Upload CSV file
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    # Read headerless CSV file
    df = pd.read_csv(uploaded_file, header=None)

    # Check number of columns
    if df.shape[1] < 2:
        st.error("The CSV file must contain at least two columns.")
        st.stop()

    # Give the columns names for display
    df = df.iloc[:, :2]
    df.columns = ["Index / Location", "Data"]

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
        "Data label (include the unit if applicable)",
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

    # --------------------------------------------------
    # Horizontal box-and-whisker plot
    # --------------------------------------------------

    st.subheader("Box-and-Whisker Plot")

    fig1, ax1 = plt.subplots(figsize=(8, 3))

    ax1.boxplot(
        data,
        vert=False,
        whis=(0, 100),       # whiskers = minimum to maximum
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

    n = len(data)

    # --------------------------------------------------
    # Recommended number of bins
    # --------------------------------------------------

    if n < 50:
        k_raw = 1.87 * (n - 1) ** 0.40 + 1
    else:
        k_raw = np.sqrt(n)

    k_opt = max(1, int(round(k_raw)))

    x_min = data.min()
    x_max = data.max()

    # Recommended bin size
    bin_size_opt = (x_max - x_min) / k_opt

    # --------------------------------------------------
    # Display recommended parameters
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
        f"Maximum data value: **{x_max:.4g}**"
    )

    st.write(
        f"Recommended bin size: **{bin_size_opt:.4g}**"
    )

    st.write(
        "Use these values as guidance when selecting an appropriate "
        "starting point and bin size for your histogram."
    )

    # --------------------------------------------------
    # Student-selected histogram parameters
    # --------------------------------------------------

    st.subheader("Choose Histogram Parameters")

    starting_x = st.number_input(
        "Starting x (lower bound of the first bin)",
        value=float(x_min),
        format="%.6g"
    )

    bin_size = st.number_input(
        "Bin size",
        min_value=0.0,
        value=float(bin_size_opt),
        format="%.6g"
    )

    # --------------------------------------------------
    # Create histogram
    # --------------------------------------------------

    if bin_size > 0:

        if starting_x > x_min:

            st.warning(
                "The starting x is greater than the minimum data "
                "value. Some observations would not be included "
                "in the histogram."
            )

        else:

            # Determine number of bins needed to include xmax
            number_of_bins = int(
                np.ceil((x_max - starting_x) / bin_size)
            )

            number_of_bins = max(1, number_of_bins)

            # Construct bin edges
            bin_edges = (
                starting_x
                + np.arange(number_of_bins + 1) * bin_size
            )

            # Account for floating-point roundoff
            if bin_edges[-1] < x_max:
                bin_edges = np.append(
                    bin_edges,
                    bin_edges[-1] + bin_size
                )

            # --------------------------------------------------
            # Calculate frequencies
            # --------------------------------------------------

            counts, edges = np.histogram(
                data,
                bins=bin_edges
            )

            # --------------------------------------------------
            # Plot histogram
            # --------------------------------------------------

            st.subheader("Histogram")

            fig2, ax2 = plt.subplots(figsize=(8, 5))

            # Unfilled histogram
            ax2.hist(
                data,
                bins=bin_edges,
                facecolor="none",
                edgecolor="black",
                linewidth=1.2
            )

            # ------------------------------------------
            # Left axis: Frequency
            # ------------------------------------------

            ax2.set_xlabel(axis_label)
            ax2.set_ylabel("Frequency")

            ax2.grid(
                True,
                axis="y",
                alpha=0.3
            )

            # ------------------------------------------
            # Right axis: Relative Frequency
            # ------------------------------------------

            ax_right = ax2.twinx()

            # Make the right axis correspond exactly
            # to frequency / total number of observations
            ymin, ymax = ax2.get_ylim()

            ax_right.set_ylim(
                ymin / n,
                ymax / n
            )

            ax_right.set_ylabel("Relative Frequency")

            # ------------------------------------------
            # Finish figure
            # ------------------------------------------

            fig2.tight_layout()

            st.pyplot(fig2)

            # --------------------------------------------------
            # Display final histogram information
            # --------------------------------------------------

            st.write(
                f"Your histogram uses **{len(bin_edges) - 1} bins** "
                f"with a bin size of **{bin_size:.4g}**."
            )

            # --------------------------------------------------
            # Download histogram
            # --------------------------------------------------

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
