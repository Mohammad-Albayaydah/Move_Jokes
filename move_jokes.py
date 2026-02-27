import requests
import re


OMDB_API_KEY = "YOUR_API_KEY"


def get_movie_data(name: str) -> dict:
    """Returns a dictionary of movie information from the OMDb API.

    Parameters
    ----------
    name : str
        The name of the movie to search for.

    Returns
    -------
    dict
        A dictionary of movie information.
    """
    baseurl = "http://www.omdbapi.com/"
    params = {
        "t": name,
        "r": "json",
        "apikey": OMDB_API_KEY
    }
    response = requests.get(baseurl, params=params)
    return response.json()



def rt_rating(movie_data: dict) -> int:
    """Returns the Rotten Tomatoes rating from a dictionary of movie information.

    Parameters
    ----------
    movie_data : dict
        A dictionary of movie information.

    Returns
    -------
    int
        The Rotten Tomatoes rating. For example, 75% would be returned as the integer 75.
    """
    for rating in movie_data.get("Ratings", []):
        if rating.get("Source") == "Rotten Tomatoes":
            value = rating.get("Value", "0%")
            return int(value.replace("%", ""))
    return -1
    


def get_joke_data(word: str) -> dict:
    baseurl = "https://icanhazdadjoke.com/search"
    headers = {"Accept": "application/json"}
    params = {"term": word, "limit": 2}
    response = requests.get(baseurl, headers=headers, params=params)
    return response.json()



def get_jokes(plot: str, verbosity=0) -> tuple[str, list[str]]:
    """Returns a tuple containing the longest word for which jokes were found
    and the joke itself. Break ties for longest word using the order in `plot`.
    Make sure that you strip punctuation from the word before you search for a joke.

    Parameters
    ----------
    plot : str
        The plot of a movie.

    verbosity : int (optional)
        If 0, no output is printed. If 1, some output is printed about which words were tried.
        Defaults to 0.

    Returns
    -------
    tuple[str, list[str]]
        A tuple containing the word that was used to search for a joke and a list of two joke strings.
    """
    words = plot.split()
    words = [w.strip(",.!;:") for w in words]

    words_sorted = sorted(words, key=len, reverse=True)

    for word in words_sorted:
        if verbosity == 1:
            print(f"Trying {word}")

        jokes_data = get_joke_data(word)
        jokes = [j["joke"] for j in jokes_data.get("results", [])]

        if jokes:
            return word, jokes

    return None, []


def highlight(word: str, sentence: str) -> str:
    """
    Highlights a specific word in a sentence by surrounding it with asterisks (**).
    The highlighting is case-insensitive.

    Args:
        word (str): The word to be highlighted.
        sentence (str): The sentence in which the word should be highlighted.

    Returns:
        str: The sentence with the specified word highlighted.
    """
    if not word:
        return sentence
    return re.sub(
        re.escape(word),
        f"**{word}**",
        sentence,
        flags=re.IGNORECASE
    )


def get_movie_jokes(movie_title: str, verbosity=0) -> str:
    info = get_movie_data(movie_title)

    if info.get("Response") == "False":
        return "Movie not found."

    word, jokes = get_jokes(info.get("Plot", ""), verbosity)

    title = info.get("Title", "Unknown Title")
    rating_value = rt_rating(info)

    if rating_value == -1:
        rating_text = "Rotten Tomatoes rating: Not available"
    else:
        rating_text = f"Rotten Tomatoes rating: {rating_value}%"

    highlighted_plot = highlight(word, info.get("Plot", ""))

    if jokes:
        highlighted_jokes = "\n".join([highlight(word, joke) for joke in jokes])

        if rating_value >= 70:
            rating_comment = "Hope they're as good as the movie!"
        elif rating_value != -1:
            rating_comment = "Hope they're better than the movie!"
        else:
            rating_comment = "Hope you like them!"

        return f"""{title}
{rating_text}

{highlighted_plot}

Speaking of **{word}**, that reminds me of some jokes.
{rating_comment}

{highlighted_jokes}
"""
    else:
        return f"""{title}
{rating_text}

{highlighted_plot}

Sorry, I couldn't find any jokes related to this movie.
"""
