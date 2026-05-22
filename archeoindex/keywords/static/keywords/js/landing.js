// LANDING PAGE -> CLICK ON LI MAKE REDIRECT TO KEYWORD PAGE
// At clicking on svg element, we aren't redirected
var fullKeywordList = document.getElementById('fullListKeywords')
fullKeywordList.addEventListener('click', e => {
    if (e.target && e.target.matches('li.keyword')) {
        e.target.children[0].click()
    }
})

// click on svg to ajax call children
fullKeywordList.addEventListener('click', e => {
    if (e.target && e.target.matches('svg.showMore')) {
        let fatherKeyword = e.target.closest('li')
        let svg = e.target
        let innerList = fatherKeyword.querySelector('ul')

        rotateSVG(svg)

        if (!innerList) {
            // generate content and show it
            fetch(`/keywords/get_children_of/${fatherKeyword.id}`)
                .then(response => response.json())
                .then(data => {
                    deployChildren(fatherKeyword, data)
                })
                .catch(error =>{
                    console.log(error)
                })
        }
        if(innerList){
            // only need to hide or show it
            showListContent(innerList)
        }
    }
})

function showListContent(list){
    const currentDisplay = list.style.display 
    list.style.display = currentDisplay == 'block' ? 'none': 'block'
}

function rotateSVG(svg) {
    const rotation = svg.getAttribute('transform')
    svg.setAttribute('transform', rotation == 'rotate(0)' ? 'rotate(90)' : 'rotate(0)')
}

function deployChildren(fatherKeyword, data) {
    const lu = document.createElement('ul')
    lu.style.display = 'block'
    fatherKeyword.appendChild(lu)
    

    data.children.forEach(child=>{
        const li = document.createElement('li');
        const a = document.createElement('a');
        li.classList.add('keyword');
        li.id = child.uri;
        a.href = child.uri;
        a.textContent = UpperCaseEveryWord(child.prefLabel.replaceAll("_", " "));
        li.appendChild(a);

        if (child.has_children) addTriangleSVG(li);
        lu.appendChild(li);
    })
}

function UpperCaseEveryWord(text){
    const words = text.split(" ")
    for (let i = 0; i != words.length; i++){
        words[i] = words[i][0].toUpperCase() + words[i].substr(1)
    }
    return words.join(' ')
}

function addTriangleSVG(li){
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    const path = document. createElementNS("http://www.w3.org/2000/svg", "path")

    svg.setAttribute('width', 20)
    svg.setAttribute('height', 20)
    svg.setAttribute('fill', 'currentColor')
    svg.setAttribute('viewBox', '0 0 15 15')
    svg.setAttribute('transform', 'rotate(0)')
    svg.classList = 'showMore'
    path.setAttributeNS(null, "d", "M6 12.796V3.204L11.481 8 6 12.796zm.659.753 5.48-4.796a1 1 0 0 0 0-1.506L6.66 2.451C6.011 1.885 5 2.345 5 3.204v9.592a1 1 0 0 0 1.659.753z")

    svg.appendChild(path)
    li.appendChild(svg)
}