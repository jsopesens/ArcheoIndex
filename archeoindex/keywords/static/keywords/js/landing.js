var fullKeywordList = document.getElementById('fullListKeywords')

// Delegated handler: button click expands/collapses; link click navigates
fullKeywordList.addEventListener('click', e => {
    if (e.target.closest('a')) return

    const btn = e.target.closest('button.expand-btn')
    if (btn) {
        toggleKeyword(btn.closest('li.keyword'))
        return
    }

    // Clicking anywhere else on the row also toggles if it has an expand button
    const li = e.target.closest('li.keyword')
    if (li && li.querySelector('button.expand-btn')) {
        toggleKeyword(li)
    }
})

// Keyboard: Space/Enter on a focused expand button triggers toggle
fullKeywordList.addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return
    const btn = e.target.closest('button.expand-btn')
    if (btn) {
        e.preventDefault()
        toggleKeyword(btn.closest('li.keyword'))
    }
})

function toggleKeyword(li) {
    const btn       = li.querySelector(':scope > .keyword-header > .expand-btn')
    const innerList = li.querySelector(':scope > ul')

    if (!innerList) {
        fetch(`/keywords/get_children_of/${li.id}`)
            .then(response => response.json())
            .then(data => {
                deployChildren(li, data)
                li.classList.add('is-open')
                if (btn) btn.setAttribute('aria-expanded', 'true')
            })
            .catch(error => console.error(error))
    } else {
        const isOpen = li.classList.contains('is-open')
        li.classList.toggle('is-open')
        innerList.style.display = isOpen ? 'none' : 'block'
        if (btn) btn.setAttribute('aria-expanded', String(!isOpen))
    }
}

function deployChildren(fatherKeyword, data) {
    const ul = document.createElement('ul')
    ul.style.display = 'block'
    fatherKeyword.appendChild(ul)

    data.children.forEach(child => {
        const li     = document.createElement('li')
        const header = document.createElement('div')
        const a      = document.createElement('a')

        li.classList.add('keyword')
        li.id = child.uri
        header.classList.add('keyword-header')
        a.href = '/' + child.uri + '/'
        a.textContent = titleCase(child.prefLabel.replaceAll('_', ' '))

        header.appendChild(a)
        if (child.has_children) {
            header.appendChild(createExpandButton(a.textContent))
        }
        li.appendChild(header)
        ul.appendChild(li)
    })
}

function createExpandButton(label) {
    const btn  = document.createElement('button')
    const svg  = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')

    btn.className = 'expand-btn'
    btn.type = 'button'
    btn.setAttribute('aria-label', `Expand ${label}`)
    btn.setAttribute('aria-expanded', 'false')

    svg.setAttribute('width', 18)
    svg.setAttribute('height', 18)
    svg.setAttribute('fill', 'currentColor')
    svg.setAttribute('viewBox', '0 0 15 15')
    svg.setAttribute('aria-hidden', 'true')
    path.setAttribute('d', 'M6 12.796V3.204L11.481 8 6 12.796zm.659.753 5.48-4.796a1 1 0 0 0 0-1.506L6.66 2.451C6.011 1.885 5 2.345 5 3.204v9.592a1 1 0 0 0 1.659.753z')

    svg.appendChild(path)
    btn.appendChild(svg)
    return btn
}

function titleCase(text) {
    return text.split(' ').map(w => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ')
}

// Auto-expand and scroll to scheme on load if URL has a hash
window.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash
    if (hash) {
        const id = hash.replace('#', '')
        const li = document.getElementById(id)
        if (li && li.querySelector('button.expand-btn')) {
            setTimeout(() => {
                toggleKeyword(li)
                li.scrollIntoView({ behavior: 'smooth', block: 'center' })
            }, 100)
        }
    }
})
