var fullKeywordList = document.getElementById('fullListKeywords')

// Delegated click handler for the whole list
fullKeywordList.addEventListener('click', e => {
    // Clicking the name link → let the browser navigate naturally
    if (e.target.closest('a')) return

    const li = e.target.closest('li.keyword')
    if (!li) return

    // Only toggle if the row has an expand arrow (i.e., has children)
    if (li.querySelector('svg.showMore')) {
        toggleKeyword(li)
    }
})

function toggleKeyword(li) {
    const innerList = li.querySelector(':scope > ul')

    if (!innerList) {
        // Children not yet loaded — fetch them
        fetch(`/keywords/get_children_of/${li.id}`)
            .then(response => response.json())
            .then(data => {
                deployChildren(li, data)
                li.classList.add('is-open')
            })
            .catch(error => console.error(error))
    } else {
        // Toggle between open and closed
        const isOpen = li.classList.contains('is-open')
        li.classList.toggle('is-open')
        innerList.style.display = isOpen ? 'none' : 'block'
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
        if (child.has_children) header.appendChild(createArrowSVG())
        li.appendChild(header)
        ul.appendChild(li)
    })
}

function titleCase(text) {
    return text.split(' ').map(w => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ')
}

function createArrowSVG() {
    const svg  = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')

    svg.setAttribute('width', 18)
    svg.setAttribute('height', 18)
    svg.setAttribute('fill', 'currentColor')
    svg.setAttribute('viewBox', '0 0 15 15')
    svg.setAttribute('aria-hidden', 'true')
    svg.classList.add('showMore')
    path.setAttribute('d', 'M6 12.796V3.204L11.481 8 6 12.796zm.659.753 5.48-4.796a1 1 0 0 0 0-1.506L6.66 2.451C6.011 1.885 5 2.345 5 3.204v9.592a1 1 0 0 0 1.659.753z')

    svg.appendChild(path)
    return svg
}
