var searchInput = document.getElementById('searchQueryInput')
var endpoint    = '/getMatchKeywords/'

searchInput.addEventListener('input', function () {
    showMatchKeywords(searchInput.value);
})

// SEARCHBAR -> CLICK ON LI ELEMENT MAKE REDIRECT TO KEYWORD PAGE

var keyword_list = document.getElementById('keywords_list')
keyword_list.addEventListener('click', e =>
    e.target.children[0].click()
)

// SEARCHBAR -> ON CLICK OUT, HIDE SUGGESTION LIST
searchInput.addEventListener('focusout', () => {
    // Make it wait in order to redirect instead of simply hide element
    setTimeout(()=>{
        keyword_list.style.display = 'none';
    }, 200)
})

searchInput.addEventListener('focusin', () => 
    keyword_list.style.display = 'block'
)

function showMatchKeywords(searchText) {
    let keywordsList = document.getElementById('keywords_list')
    let keywordsContainer = document.getElementById('navBarContainer')
    // GET MODE
    // search input with only whitespaces generates errors on the HTTP request
    if (searchText.trim() != '') {
        fetch(endpoint + searchText)
            .then(keywordsList.innerHTML = '')
            .then(response => response.json())
            // .then(response => console.log(response))
            .then(data => convertToListElements(data.keywords))
    } else
        keywordsContainer.style.display = 'none'
}

function convertToListElements(data) {
    data.forEach(element => {
        const li = document.createElement('li')
        const a = document.createElement('a')
        li.classList.add('keyword_suggestion')
        a.href = element.uri
        a.innerHTML = element.label
        li.appendChild(a)
        document.getElementById('keywords_list').appendChild(li)
    });
    showSuggestions()
}

function showSuggestions() {
    const keywordDOM = document.getElementById('navBarContainer')
    const keywordsList = document.getElementById('keywords_list')

    keywordDOM.style.display =
        (keywordsList.childElementCount === 0 || searchInput.value == '') ?
            'none' :
            'block'
}
