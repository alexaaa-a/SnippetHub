document.getElementById('sort-snippets').addEventListener('click', function () {
    const snippetContainer = document.querySelector('.row');
    const snippets = Array.from(snippetContainer.children);

    snippets.sort((a, b) => {
        const titleA = a.querySelector('.card-title').textContent.trim();
        const titleB = b.querySelector('.card-title').textContent.trim();
        return titleA.localeCompare(titleB);
    });

    snippetContainer.innerHTML = '';
    snippets.forEach(snippet => snippetContainer.appendChild(snippet));
});
