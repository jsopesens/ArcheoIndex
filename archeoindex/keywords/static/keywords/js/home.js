const homeSearchInput = document.getElementById('homeSearchQueryInput')
const homeDropdown    = document.getElementById('homeNavBarContainer')
const homeSuggestions = document.getElementById('homeKeywords_list')
const homeEndpoint    = '/getMatchKeywords/'

let homeDebounceTimer = null

// Prevent form submit (Enter key) from reloading the page
const homeForm = homeSearchInput.closest('form')
if (homeForm) {
    homeForm.addEventListener('submit', e => e.preventDefault())
}

// Search as user types, debounced to avoid hammering the server
homeSearchInput.addEventListener('input', () => {
    clearTimeout(homeDebounceTimer)
    homeDebounceTimer = setTimeout(() => searchHome(homeSearchInput.value), 220)
})

// Re-show existing results when the user refocuses the input
homeSearchInput.addEventListener('focusin', () => {
    if (homeSuggestions.childElementCount > 0) showHomeDropdown()
})

// Hide dropdown on blur (delay to allow a click on a suggestion to fire first)
homeSearchInput.addEventListener('focusout', () => {
    setTimeout(hideHomeDropdown, 200)
})

// Navigate when a suggestion is clicked
homeDropdown.addEventListener('click', e => {
    const li = e.target.closest('li.keyword_suggestion')
    if (li) {
        const a = li.querySelector('a')
        if (a) window.location.href = a.href
    }
})

function searchHome(text) {
    if (!text.trim()) {
        hideHomeDropdown()
        return
    }

    fetch(homeEndpoint + encodeURIComponent(text.trim()))
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            return response.json()
        })
        .then(data => renderHomeSuggestions(data.keywords))
        .catch(err => console.error('Search error:', err))
}

function renderHomeSuggestions(keywords) {
    homeSuggestions.innerHTML = ''

    if (!keywords || keywords.length === 0) {
        hideHomeDropdown()
        return
    }

    keywords.forEach(keyword => {
        const li = document.createElement('li')
        const a  = document.createElement('a')
        li.classList.add('keyword_suggestion')
        a.href      = '/' + keyword.uri + '/'
        a.textContent = keyword.label
        li.appendChild(a)
        homeSuggestions.appendChild(li)
    })

    showHomeDropdown()
}

function showHomeDropdown() { homeDropdown.style.display = 'block' }
function hideHomeDropdown()  { homeDropdown.style.display = 'none'  }
