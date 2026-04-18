searchInput = document.getElementById("search");
cards = document.querySelectorAll(".card");

searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();

    cards.forEach(element => {
        const text = element.textContent.toLowerCase();
        element.style.display = text.includes(query) ? "" : "none";
    })
})

async function preview(query) {

    const response = await fetch(
        `https://itunes.apple.com/search?term=${query}&media=music&limit=1`
    );

    const data = await response.json();
    const previewUrl = data.results[0]?.previewUrl;

    if (!previewUrl) {
        return;
    }

    if (window._currentPreview) {
        window._currentPreview.pause();
        window._currentPreview.currentTime = 0;
    }

    const audio = new Audio(previewUrl);
    window._currentPreview = audio;

    const maxSeconds = 30;
    setTimeout(() => {
        audio.pause()
        audio.currentTime = 0;
    }, maxSeconds * 1000)

    audio.onended = () => {};
    audio.play();
}

document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", function(e) {
        e.preventDefault();

        if (window._currentPreview && !window._currentPreview.paused) {
            window._currentPreview.pause();
            window._currentPreview.currentTime = 0;
            return;
        } else {
            const query = encodeURIComponent(e.target.name);
            
            preview(query);
        }
    })
})