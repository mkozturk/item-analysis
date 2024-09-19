import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
samplefile = "data/sample1.xlsx"

def get_key(df):
    return df.iloc[0, :]

def get_responses(df):
    return df.iloc[1:,:]

st.set_page_config(
    page_title="Item Analysis App",
    page_icon="img/icon.svg",
    layout="centered",
    initial_sidebar_state="expanded",
)
# Initial State
def initial_state():
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'datasource' not in st.session_state:
        st.session_state['datasource'] = None # None, "sample", or "upload"

initial_state()

st.image("img/pencil_and_test.png", use_column_width=True)

"# Test Item Analysis Reporting Tool"

with st.sidebar:
    "## About 👩🏻‍💻"
    "This application takes the responses of a multiple-choice test and calculates statistics of test items' difficulty and discriminative power."

    "## Demo 🕹️"
    "Click the button to load the sample response set and see its analysis results."
    def sample_click():
        st.session_state.datasource = "sample"
        st.session_state.df = None
    load_sample = st.button("Load Sample", on_click=sample_click)

    "## Upload your data 📂"
    "Single-sheet Excel or CSV file. Students in rows, items in columns. Solution key in the first row."
    def upload_change():
        st.session_state.datasource = "upload"
        st.session_state.df = None
    uploaded_file = st.file_uploader("Upload your data file", type=["xlsx","csv"], label_visibility="hidden", on_change=upload_change)
    
    "## Settings 🛠️"
    difficulty_hard, difficulty_medium = st.select_slider(
        "Set difficulty levels",
        options=range(0,105,5), 
        value=(20,70))
    st.dataframe(
        pd.DataFrame(
            [f"0 to {difficulty_hard}", f"{difficulty_hard} to {difficulty_medium}", f"{difficulty_medium} to 100"],
            index=["Hard","Medium","Easy"]
            ).T,
            hide_index=True
    )
    disc_fair,disc_good = st.select_slider(
        "Set discrimination levels",
        options=[round(i/10,1) for i in range(11)],
        value=(0.2,0.4))
    st.dataframe(
        pd.DataFrame(
            [f"(-1.0) to {disc_fair}", f"{disc_fair} to {disc_good}", f"{disc_good} to 1.0"],
            index=["Poor","Fair","Good"]
            ).T,
            hide_index=True
    )
    
    st.divider()
    "Created and maintained by [Kaan Öztürk](https://mkozturk.com)"
    "Project site: https://github.com/mkozturk/item-analysis"

report, help = st.tabs(["Report","Help"])

with help:
    with st.expander(label="How should the data be formatted?"):
        """
        The input file should have the responses arranged in rows. Eevery column corresponds to one response item (exam question).

        The first row can be used as column headings, and the first column can be used for labeling (e.g., student name, ID, etc.). If labels are omitted in data, the report will use automatically generated labels.

        The input table cannot have more than one row or column as labels. In other words, responses must begin either in the first or the second row, or in the first or second column.

        The solution key **must** be on the first row of responses (after column headings, if any).
        """
    with st.expander("What kind of responses are accepted? A-D, T/F,...?"):
        """
        Responses can be anything. The program does not care how the responses are labeled, 
        so it will work with {A,B,C,D}, or {T,F}, or {a,b,c,d,e}, or any mixture of them.

        However, "a" and "A" will be treated as different responses. If your data has both lowercase and uppercase responses, correct them before uploading.
        """
    with st.expander(label="Is my data secure?"):
        """
        This app does not store the data you upload, nor does it track its users. The data is discarded when you close the page.

        As an additional privacy measure, you can remove identifying columns from the data before uploading. The report will generate automatic labels.
        """
    with st.expander(label="What if my test has both multiple-choice and true-false questions?"):
        """
        The report handles such tests without problems. Each item will be evaluated separately according its own response set.
        You can have A-D responses, A-E responses, T/F responses, or any other discrete set of responses mixed in your test.
        """
    with st.expander(label="Can I analyze open-ended questions?"):
        """Item analysis algorithms can work only with responses that are right or wrong. If you are not giving partial credit,
        you can encode the responses as T/F (or 1/0, or any other binary code as you please), and run the analysis on that."""

    with st.expander(label="How can I analyze different booklets of the same exam?"):
        """The analysis of several booklets of the same exam where responses are shuffled randomly, is not implemented in this app. 
        In order to analyze such an exam, you would need to un-shuffle the responses and collect them in a single table.
        """
    
    with st.expander(label="How is item difficulty calculated?"):
        """The difficulty of an item is defined as the fraction of correct answers, multiplied by 100."""
    
    with st.expander(label="How is an item's discrimination index calculated?"):
        """The discrimination index (DI) of an item can be defined in several different ways. Here we use a simple but useful form: 
        Count the correct answers to that item in the top 25% group and in the bottom 25% group, evaluated on the overall exam score.
        The DI is the difference between them, divided by the number of students in one of these groups."""

with report:
    #### Wait until the data is loaded
    if st.session_state.df is None:
        if st.session_state.datasource=="sample":
            df = pd.read_excel(samplefile, header=None)
        elif st.session_state.datasource=="upload":
            if uploaded_file is None: # occurs when the uploaded file is removed
                st.stop()
            if uploaded_file.name.endswith("xlsx"):
                df = pd.read_excel(uploaded_file, header=None)
            if uploaded_file.name.endswith("csv"):
                df = pd.read_csv(uploaded_file, header=None)
        else:
            st.stop()
            
    ##### ------  PREVIEW THE DATA SHEET -----
    st.write("## Data Preview 📄")
    st.write("*Check the correctness of your data. Edit and reupload if necessary.*")

    labels_in_first_row = st.checkbox("Use first row as column labels", value=True)
    idx_first_col = st.checkbox("Use first column as index", value=True)
    if labels_in_first_row:
        df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    else:
        df = df.set_axis([f"Q{i+1:d}" for i in df.columns],axis=1)
    
    if idx_first_col:
        df = df.set_index(df.columns[0])
    else:
        df = df.set_axis([f"S{i+1:d}" for i in df.index])

    if not df.index.is_unique:
        st.error("Duplicate index values found. Try unchecking 'Use first column as index' or review your input.")
        st.stop()
    if not df.columns.is_unique:
        st.error("Duplicate column names found. Try unchecking 'Use first row as column labels'")
        st.stop()
    
    st.dataframe(df) # preview the data sheet

    # try:
    #     st.dataframe(df) # preview the data sheet
    # except ValueError as e:
    #     if "Duplicate column names found" in e.__str__():
    #         st.error("Error reading column names. Try unchecking 'Use first row as column labels'")
    #         st.stop()


    key = get_key(df)
    responses = get_responses(df)
    grading = (responses==key) # table of boolean values showing correctness. NaN are possible.

    ##### -------- STUDENT SCORES -------

    st.write("## Student scores 👨‍🎓")
    """Scores and their statistics."""
    scores = grading.sum(axis=1)
    empty = responses.isna().sum(axis=1)
    incorrect = len(responses.columns) - scores - empty

    col1, col2 = st.columns([0.4,0.6])
    col1.dataframe(pd.DataFrame({"correct":scores,"incorrect":incorrect, "empty":empty}))
    col2.write(f"Mean score: {scores.mean():.2f}")
    col2.write(f"Score standard deviation: {scores.std():.2f}")
    fig = plt.figure()
    plt.hist(scores, bins=range(scores.min(), scores.max()+2), align="left",color="C0",rwidth=0.9)

    plt.title("Histogram")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    col2.write(fig)


    # Upper and lower quartile students
    sortedscores = scores.sort_values(ascending=False)
    n = len(scores)
    dfcomb = pd.merge(pd.DataFrame({"score":scores}), df, left_index=True, right_index=True)

    upper_quartile_idx = sortedscores[:(n//4)].index
    lower_quartile_idx = sortedscores[-(n//4):].index

    col1, col2 = st.columns(2)
    col1.write("Upper quartile students")
    col1.dataframe(dfcomb.loc[upper_quartile_idx])
    col2.write("Lower quartile students")
    col2.dataframe(dfcomb.loc[lower_quartile_idx])

    ##### --------- ITEM ANALYSIS ----------
    st.write("## Item Analysis 🔬")
    difficulty = grading.mean(axis=0)*100
    discrimination_index = (grading.loc[upper_quartile_idx].sum() - grading.loc[lower_quartile_idx].sum()) / (len(upper_quartile_idx))

    difficulty_category = pd.cut(difficulty, bins=(0, difficulty_hard, difficulty_medium, 100), labels=("hard","medium","easy"))
    discrimination_category = pd.cut(discrimination_index, bins=(-1,disc_fair,disc_good,1), labels=("poor","fair","good"))
    itemdf = pd.DataFrame(
            {"key":key,
            "difficulty":difficulty.astype(int),
            "difficulty level":difficulty_category,
            "discrimination":discrimination_index.round(2),
            "discrimination level": discrimination_category,
            }
        )

    """The difficulty score (percentage of correct answers) and discrimination index for each item.
    """
    st.dataframe(itemdf)

    # Discrimination-difficulty matrix

    disc_diff = (
        itemdf
        .reset_index()
        [["index","difficulty level","discrimination level"]]
        .rename(columns={"index":"item"})
        .pivot_table(index="discrimination level", columns="difficulty level", aggfunc=lambda x:", ".join(x))
        .stack()
        .reindex(
            (
            ("poor","easy"),("poor","medium"),("poor","hard"),
            ("fair","easy"),("fair","medium"),("fair","hard"),
            ("good","easy"),("good","medium"),("good","hard")
            ))
        .unstack(sort=False)
        .fillna("-")
    )
    disc_diff.columns = disc_diff.columns.droplevel(0)

    """Items broken by difficulty level (easy, medium, hard) and discrimination level (poor, fair, good)."""
    st.table(disc_diff)

    ##### --------- DISTRACTOR ANALYSIS ----
    "## Distractor Analysis 📊"
    """*Frequency of every choice for each item. Correct response shown in bold.*"""
    # generate a table of frequency of choices in each item
    choice_freqs = (
        pd.DataFrame(
            [c[1].value_counts().sort_index().to_dict() for c in responses.items()],
            index=responses.columns
            )
        .fillna(0)
        .astype(int)
    )

    styler = choice_freqs.style
    for k, v in key.items():
        styler.set_properties(**{"font-weight":"bold"}, subset=(k, v))
    st.table(styler)