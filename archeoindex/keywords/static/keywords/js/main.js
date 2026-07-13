const searchInput = document.getElementById('searchQueryInput')
const dropdown    = document.getElementById('navBarContainer')
const suggestions = document.getElementById('keywords_list')
const endpoint    = '/getMatchKeywords/'

let debounceTimer = null

// Prevent form submit (Enter key) from reloading the page
searchInput.closest('form').addEventListener('submit', e => e.preventDefault())

// Search as user types, debounced to avoid hammering the server
searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => search(searchInput.value), 220)
})

// Re-show existing results when the user refocuses the input
searchInput.addEventListener('focusin', () => {
    if (suggestions.childElementCount > 0) showDropdown()
})

// Hide dropdown on blur (delay to allow a click on a suggestion to fire first)
searchInput.addEventListener('focusout', () => {
    setTimeout(hideDropdown, 200)
})

// Navigate when a suggestion is clicked
dropdown.addEventListener('click', e => {
    const li = e.target.closest('li.keyword_suggestion')
    if (li) {
        const a = li.querySelector('a')
        if (a) window.location.href = a.href
    }
})

function search(text) {
    if (!text.trim()) {
        hideDropdown()
        return
    }

    fetch(endpoint + text.trim())
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            return response.json()
        })
        .then(data => renderSuggestions(data.keywords))
        .catch(err => console.error('Search error:', err))
}

function renderSuggestions(keywords) {
    suggestions.innerHTML = ''

    if (!keywords || keywords.length === 0) {
        hideDropdown()
        return
    }

    keywords.forEach(keyword => {
        const li = document.createElement('li')
        const a  = document.createElement('a')
        li.classList.add('keyword_suggestion')
        a.href      = '/' + keyword.uri + '/'
        a.textContent = keyword.label
        li.appendChild(a)
        suggestions.appendChild(li)
    })

    showDropdown()
}

function showDropdown() { dropdown.style.display = 'block' }
function hideDropdown()  { dropdown.style.display = 'none'  }
