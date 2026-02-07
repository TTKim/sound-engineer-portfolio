// YouTube 썸네일 URL 생성 함수 (여러 해상도 시도)
function getThumbnailUrl(youtubeId) {
    // maxresdefault가 없으면 hqdefault로 폴백
    return `https://img.youtube.com/vi/${youtubeId}/maxresdefault.jpg`;
}

// 썸네일 로드 실패 시 대체 이미지 로드 (개선된 버전)
function loadThumbnailWithFallback(img, youtubeId) {
    if (!youtubeId || youtubeId.length < 11) {
        img.style.display = 'none';
        return;
    }
    
    // YouTube 썸네일 URL 형식 (여러 해상도 시도)
    const fallbackUrls = [
        `https://img.youtube.com/vi/${youtubeId}/maxresdefault.jpg`,
        `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg`,
        `https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`,
        `https://img.youtube.com/vi/${youtubeId}/sddefault.jpg`,
        `https://img.youtube.com/vi/${youtubeId}/default.jpg`
    ];
    
    let currentIndex = 0;
    let hasLoaded = false;
    let timeoutId = null;
    
    function tryNext() {
        if (hasLoaded) return;
        
        if (currentIndex < fallbackUrls.length) {
            const testImg = new Image();
            
            // 타임아웃 설정 (5초)
            timeoutId = setTimeout(() => {
                if (!hasLoaded) {
                    testImg.onload = null;
                    testImg.onerror = null;
                    currentIndex++;
                    if (currentIndex < fallbackUrls.length) {
                        tryNext();
                    } else {
                        img.style.display = 'none';
                    }
                }
            }, 5000);
            
            testImg.onload = function() {
                clearTimeout(timeoutId);
                if (!hasLoaded) {
                    hasLoaded = true;
                    img.src = fallbackUrls[currentIndex];
                    img.style.display = 'block';
                    img.style.opacity = '0';
                    // 페이드 인 효과
                    setTimeout(() => {
                        img.style.transition = 'opacity 0.3s ease';
                        img.style.opacity = '1';
                    }, 10);
                }
            };
            
            testImg.onerror = function() {
                clearTimeout(timeoutId);
                currentIndex++;
                if (currentIndex < fallbackUrls.length) {
                    tryNext();
                } else {
                    // 모든 썸네일이 실패하면 기본 그라데이션 배경 사용
                    img.style.display = 'none';
                }
            };
            
            testImg.src = fallbackUrls[currentIndex];
        } else {
            img.style.display = 'none';
        }
    }
    
    // 첫 번째 URL 시도
    tryNext();
}

function loadImageDirectly(img, imageUrl) {
    if (!imageUrl) {
        img.style.display = 'none';
        return;
    }
    img.style.display = 'block';
    img.style.opacity = '0';
    img.onload = () => {
        img.style.transition = 'opacity 0.3s ease';
        img.style.opacity = '1';
    };
    img.onerror = () => {
        img.style.display = 'none';
    };
    img.src = imageUrl;
}

function loadThumbnailForSong(img, song) {
    if (song.thumbnailUrl) {
        loadImageDirectly(img, song.thumbnailUrl);
        return;
    }
    loadThumbnailWithFallback(img, song.youtubeId);
}

// 아티스트별 음악 데이터 (CSV 로드 실패 시 폴백)
const fallbackArtistsData = {
    "검정치마": {
        name: "검정치마",
        genre: "Indie Rock",
        description: "몽환적이고 감성적인 인디 록 밴드",
        songs: [
            {
                id: 1,
                title: "Hollywood",
                genre: "Indie Rock",
                year: 2012,
                category: "Mixing",
                description: "검정치마의 대표곡으로, 몽환적이고 감성적인 멜로디가 특징입니다. 독특한 보컬 톤과 기타 사운드가 조화를 이룹니다.",
                youtubeId: "uuGtrxDsrws"
            },
            {
                id: 2,
                title: "기다린 만큼 더",
                genre: "Indie Rock",
                year: 2013,
                category: "Digital Editing",
                description: "서정적이고 따뜻한 감성을 담은 곡입니다. 기다림의 감정을 아름답게 표현한 검정치마의 명곡입니다.",
                youtubeId: "ItAXIBzMxn8"
            },
            {
                id: 3,
                title: "나랑 아니면",
                genre: "Indie Rock",
                year: 2014,
                category: "Recording",
                description: "강렬한 기타 리프와 감성적인 보컬이 어우러진 곡입니다. 검정치마 특유의 독창적인 사운드를 느낄 수 있습니다.",
                youtubeId: "c88_wmVua3s"
            },
            {
                id: 7,
                title: "Everything",
                genre: "Indie Rock",
                year: 2015,
                category: "Mixing",
                description: "검정치마의 감성적인 발라드 곡입니다. 부드러운 멜로디와 진심 어린 가사가 마음을 울립니다.",
                youtubeId: "HXV5aZaBLDo"
            }
        ]
    },
    "국카스텐": {
        name: "국카스텐",
        genre: "Rock",
        description: "강렬하고 에너지 넘치는 록 밴드",
        songs: [
            {
                id: 4,
                title: "이방인",
                genre: "Rock",
                year: 2009,
                category: "Recording",
                description: "국카스텐의 데뷔곡으로, 강렬한 록 사운드와 감성적인 가사가 특징입니다. 한국 인디 록의 대표작 중 하나입니다.",
                youtubeId: "zSOeZ7-PSEI"
            },
            {
                id: 5,
                title: "플레어 (Flare)",
                genre: "Rock",
                year: 2011,
                category: "Broadcasting",
                description: "에너지 넘치는 록 사운드와 강렬한 드럼 비트가 인상적인 곡입니다. 국카스텐의 역동적인 무대 퍼포먼스를 느낄 수 있습니다.",
                youtubeId: "n6W8c4E93_s"
            },
            {
                id: 6,
                title: "Faust",
                genre: "Rock",
                year: 2013,
                category: "Mixing",
                description: "국카스텐의 대표곡 중 하나로, 강렬한 기타 사운드와 파워풀한 보컬이 돋보이는 곡입니다.",
                youtubeId: "5hiaMxGDI-w"
            },
            {
                id: 10,
                title: "거울",
                genre: "Rock",
                year: 2015,
                category: "Digital Editing",
                description: "국카스텐의 감성적인 록 발라드입니다. 강렬한 사운드와 함께 깊이 있는 가사가 인상적입니다.",
                youtubeId: "YWDKnqOZ3ro"
            }
        ]
    }
};

let artistsData = JSON.parse(JSON.stringify(fallbackArtistsData));
let mediaMatchMap = {};

// 현재 보기 상태 관리
let currentView = 'artists'; // 'artists' 또는 'songs'
let currentArtist = null;
let currentFilter = 'category'; // 'category', 'artist', 'genre', 'year'
const filterContext = {
    category: {
        title: '작업유형별 보기',
        description: 'Digital Editing, Mixing, Broadcasting, Recording 기준으로 작업물을 탐색합니다.'
    },
    artist: {
        title: '아티스트별 보기',
        description: '아티스트 카드를 선택해 관련 작업곡을 한 번에 확인합니다.'
    },
    genre: {
        title: '장르별 보기',
        description: '장르를 기준으로 사운드 톤과 작업 성향을 빠르게 훑어볼 수 있습니다.'
    },
    year: {
        title: '연도별 보기',
        description: '연도 흐름으로 작업 이력을 확인하고 시기별 결과물을 비교할 수 있습니다.'
    }
};

function parseCsvLine(line) {
    const cells = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        const next = line[i + 1];
        
        if (char === '"' && inQuotes && next === '"') {
            current += '"';
            i++;
            continue;
        }
        
        if (char === '"') {
            inQuotes = !inQuotes;
            continue;
        }
        
        if (char === ',' && !inQuotes) {
            cells.push(current.trim());
            current = '';
            continue;
        }
        
        current += char;
    }
    
    cells.push(current.trim());
    return cells;
}

function normalizeMediaKey(value) {
    return String(value || '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, ' ');
}

function makeMediaKey(artist, album, title) {
    return `${normalizeMediaKey(artist)}|${normalizeMediaKey(album)}|${normalizeMediaKey(title)}`;
}

async function loadMediaMatchMap() {
    try {
        const response = await fetch('portfolio_media_map.json');
        if (!response.ok) return;
        const payload = await response.json();
        const items = Array.isArray(payload.items) ? payload.items : [];
        const built = {};
        items.forEach(item => {
            if (!item || !item.key) return;
            built[item.key] = item;
        });
        mediaMatchMap = built;
    } catch (error) {
        mediaMatchMap = {};
    }
}

function mapWorkPartToCategory(workPart) {
    const part = String(workPart || '').trim().toLowerCase();
    if (!part) return null;
    if (part.includes('믹싱') || part.includes('mix')) return 'Mixing';
    if (part.includes('녹음') || part.includes('record')) return 'Recording';
    if (part.includes('방송') || part.includes('broadcast')) return 'Broadcasting';
    if (part.includes('튠') || part.includes('edit')) return 'Digital Editing';
    return 'Other';
}

function parseWorkCategories(workText) {
    const workParts = (workText || '')
        .split(',')
        .map(part => part.trim())
        .filter(Boolean);
    
    const categories = [];
    workParts.forEach(part => {
        const mapped = mapWorkPartToCategory(part);
        if (mapped && !categories.includes(mapped)) {
            categories.push(mapped);
        }
    });
    
    return categories.length ? categories : ['Other'];
}

function inferYearValue(...texts) {
    const yearRegex = /(19|20)\d{2}/;
    for (const text of texts) {
        const match = String(text || '').match(yearRegex);
        if (match) return Number(match[0]);
    }
    return '미상';
}

function formatYearLabel(year) {
    return Number.isFinite(Number(year)) ? `${year}년` : String(year || '미상');
}

function isAllTracksTitle(titleRaw) {
    const normalized = String(titleRaw || '').trim();
    if (!normalized) return false;
    if (normalized === '전곡') return true;
    return /^(\d+\s*,\s*)+\d+$/.test(normalized);
}

function buildArtistsDataFromCsv(csvText) {
    const lines = csvText
        .split(/\r?\n/)
        .map(line => line.trim())
        .filter(Boolean);
    
    if (lines.length < 2) return null;
    
    const headers = parseCsvLine(lines[0]);
    const columnIndex = {
        artist: headers.indexOf('Artist'),
        album: headers.indexOf('Album'),
        title: headers.indexOf('Title'),
        work: headers.indexOf('Work'),
        note: headers.indexOf('note')
    };
    
    if (columnIndex.artist === -1) return null;
    
    const built = {};
    let songId = 1;
    
    for (let i = 1; i < lines.length; i++) {
        const row = parseCsvLine(lines[i]);
        const artistName = (row[columnIndex.artist] || '').trim();
        if (!artistName) continue;
        
        const album = (row[columnIndex.album] || '').trim();
        const titleRaw = (row[columnIndex.title] || '').trim();
        const work = (row[columnIndex.work] || '').trim();
        const note = (row[columnIndex.note] || '').trim();
        
        if (!built[artistName]) {
            built[artistName] = {
                name: artistName,
                genre: 'Session Work',
                description: '포트폴리오 작업',
                songs: [],
                _albumSet: new Set(),
                _categorySet: new Set()
            };
        }
        
        const workCategories = parseWorkCategories(work);
        const primaryCategory = workCategories[0];
        const isAllTracks = isAllTracksTitle(titleRaw);
        const title = isAllTracks
            ? (album || '전곡 작업')
            : (titleRaw || (album ? `${album} 작업물` : `작업물 ${songId}`));
        const year = inferYearValue(album, titleRaw, note);
        const descriptionParts = [];
        const mediaKey = makeMediaKey(artistName, album, titleRaw);
        const media = mediaMatchMap[mediaKey] || null;
        
        if (album) descriptionParts.push(`앨범/프로젝트: ${album}`);
        if (isAllTracks) {
            descriptionParts.push('범위: 전곡 (앨범 전체 작업)');
            if (titleRaw && titleRaw !== '전곡') {
                descriptionParts.push(`원본 표기: ${titleRaw}`);
            }
        }
        if (work) descriptionParts.push(`작업: ${work}`);
        if (note) descriptionParts.push(`비고: ${note}`);
        
        built[artistName].songs.push({
            id: songId++,
            title,
            genre: workCategories.join(' / '),
            year,
            category: primaryCategory,
            categories: workCategories,
            workDisplay: work || workCategories.join(', '),
            description: descriptionParts.join(' | ') || '포트폴리오 작업물',
            youtubeId: media?.youtube_id || '',
            thumbnailUrl: media?.cover_url || media?.youtube_thumbnail || ''
        });
        
        if (album) built[artistName]._albumSet.add(album);
        workCategories.forEach(cat => built[artistName]._categorySet.add(cat));
    }
    
    const artistNames = Object.keys(built);
    if (!artistNames.length) return null;
    
    artistNames.forEach(name => {
        const artist = built[name];
        const categories = Array.from(artist._categorySet);
        const albumCount = artist._albumSet.size;
        
        artist.genre = categories.join(' / ') || 'Session Work';
        artist.description = `${artist.songs.length}개 작업 · ${albumCount}개 프로젝트`;
        
        delete artist._albumSet;
        delete artist._categorySet;
    });
    
    return built;
}

async function loadPortfolioDataFromCsv() {
    try {
        await loadMediaMatchMap();
        const response = await fetch('Portfolio_list.csv');
        if (!response.ok) return;
        
        const csvText = await response.text();
        const built = buildArtistsDataFromCsv(csvText);
        if (built) {
            artistsData = built;
        }
    } catch (error) {
        // CSV 로드 실패 시 폴백 데이터 유지
    }
}

function updateHeaderMeta(contextText = '전체 아카이브') {
    const headerMeta = document.getElementById('headerMeta');
    if (!headerMeta) return;
    
    const allSongs = getAllSongs();
    const artistsCount = Object.keys(artistsData).length;
    const genresCount = Object.keys(getSongsByGenre()).length;
    const yearsCount = Object.keys(getSongsByYear()).length;
    
    headerMeta.innerHTML = `
        <span class="meta-pill"><strong>${allSongs.length}</strong><span>작업물</span></span>
        <span class="meta-pill"><strong>${artistsCount}</strong><span>아티스트</span></span>
        <span class="meta-pill"><strong>${genresCount}</strong><span>장르</span></span>
        <span class="meta-pill"><strong>${yearsCount}</strong><span>연도</span></span>
        <span class="meta-pill context"><span>현재 보기</span><strong>${contextText}</strong></span>
    `;
}

function updateViewIntro(title, description) {
    const viewTitle = document.getElementById('viewTitle');
    const viewDescription = document.getElementById('viewDescription');
    
    if (viewTitle) viewTitle.textContent = title;
    if (viewDescription) viewDescription.textContent = description;
}

function updateOverviewContext(filterMode) {
    const context = filterContext[filterMode] || filterContext.category;
    updateViewIntro(context.title, context.description);
    updateHeaderMeta(context.title.replace(' 보기', ''));
}

// 모든 노래 데이터 수집
function getAllSongs() {
    const allSongs = [];
    Object.values(artistsData).forEach(artist => {
        artist.songs.forEach(song => {
            allSongs.push({ ...song, artist: artist.name });
        });
    });
    return allSongs;
}

// 장르별로 그룹화
function getSongsByGenre() {
    const songs = getAllSongs();
    const grouped = {};
    songs.forEach(song => {
        if (!grouped[song.genre]) {
            grouped[song.genre] = [];
        }
        grouped[song.genre].push(song);
    });
    return grouped;
}

// 연도별로 그룹화
function getSongsByYear() {
    const songs = getAllSongs();
    const grouped = {};
    songs.forEach(song => {
        if (!grouped[song.year]) {
            grouped[song.year] = [];
        }
        grouped[song.year].push(song);
    });
    return grouped;
}

// 작업 유형별로 그룹화
function getSongsByCategory() {
    const songs = getAllSongs();
    const grouped = {};
    songs.forEach(song => {
        const categories = Array.isArray(song.categories) && song.categories.length
            ? song.categories
            : [song.category || 'Other'];
        categories.forEach(category => {
            if (!grouped[category]) {
                grouped[category] = [];
            }
            grouped[category].push(song);
        });
    });
    return grouped;
}

function getCategoryThumbnailLayout(songCount) {
    if (songCount <= 1) return { cols: 1, rows: 1 };
    if (songCount === 2) return { cols: 2, rows: 1 };
    if (songCount === 3) return { cols: 3, rows: 1 };
    if (songCount <= 4) return { cols: 2, rows: 2 };
    if (songCount <= 6) return { cols: 3, rows: 2 };
    return { cols: 3, rows: 3 };
}

function shuffleSongs(songs) {
    const copied = [...songs];
    for (let i = copied.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copied[i], copied[j]] = [copied[j], copied[i]];
    }
    return copied;
}

function getCategoryThumbnailSongs(songs, cellCount) {
    if (!songs.length || cellCount <= 0) return [];
    
    const shuffled = shuffleSongs(songs);
    const picked = shuffled.slice(0, Math.min(cellCount, shuffled.length));
    
    // 셀이 남는 경우 일부 썸네일을 반복 사용해 빈칸 없이 채움
    while (picked.length < cellCount) {
        picked.push(shuffled[Math.floor(Math.random() * shuffled.length)]);
    }
    
    return picked;
}

// 필터 모드에 따라 카드 생성
function createCardsByFilter(filterMode) {
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid';
    updateOverviewContext(filterMode);
    
    if (filterMode === 'artist') {
        createArtistCards();
    } else if (filterMode === 'genre') {
        createGenreCards();
    } else if (filterMode === 'year') {
        createYearCards();
    } else if (filterMode === 'category') {
        createCategoryCards();
    }
}

// 아티스트 카드 생성
function createArtistCards() {
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid';
    
    Object.values(artistsData).forEach(artist => {
        const card = document.createElement('div');
        card.className = 'artist-card';
        card.dataset.artistName = artist.name;
        
        // 대표곡 썸네일 (최대 4개)
        const featuredSongs = artist.songs.slice(0, 4);
        const thumbnailsHtml = featuredSongs.map((song, index) => 
            `<div class="featured-thumbnail" style="z-index: ${4 - index}">
                <img src="" alt="${song.title}" data-youtube-id="${song.youtubeId}">
            </div>`
        ).join('');
        
        card.innerHTML = `
            <div class="artist-thumbnails">
                ${thumbnailsHtml}
            </div>
            <div class="card-info">
                <div class="card-title">${artist.name}</div>
                <div class="card-artist">${artist.genre}</div>
                <div class="card-description">${artist.description}</div>
                <div class="song-count">${artist.songs.length}곡</div>
            </div>
        `;
        
        // 썸네일 이미지 로드
        card.querySelectorAll('.featured-thumbnail img').forEach((img, index) => {
            loadThumbnailForSong(img, featuredSongs[index]);
        });
        
        // 클릭 이벤트
        card.addEventListener('click', () => {
            showArtistSongs(artist.name);
        });
        
        // 터치 피드백
        card.addEventListener('touchstart', function() {
            this.style.opacity = '0.8';
        }, { passive: true });
        
        card.addEventListener('touchend', function() {
            this.style.opacity = '1';
        }, { passive: true });
        
        grid.appendChild(card);
    });
}

// 장르별 카드 생성
function createGenreCards() {
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid';
    
    const genreGroups = getSongsByGenre();
    const sortedGenres = Object.keys(genreGroups).sort();
    
    sortedGenres.forEach(genre => {
        const songs = genreGroups[genre];
        const card = document.createElement('div');
        card.className = 'genre-card';
        card.dataset.genre = genre;
        
        // 대표곡 썸네일 (최대 4개)
        const featuredSongs = songs.slice(0, 4);
        const thumbnailsHtml = featuredSongs.map((song, index) => 
            `<div class="featured-thumbnail" style="z-index: ${4 - index}">
                <img src="" alt="${song.title}" data-youtube-id="${song.youtubeId}">
            </div>`
        ).join('');
        
        card.innerHTML = `
            <div class="artist-thumbnails">
                ${thumbnailsHtml}
            </div>
            <div class="card-info">
                <div class="card-title">${genre}</div>
                <div class="card-artist">${songs.length}곡</div>
                <div class="card-description">${songs.map(s => s.artist).filter((v, i, a) => a.indexOf(v) === i).join(', ')}</div>
                <div class="song-count">${songs.length}곡</div>
            </div>
        `;
        
        // 썸네일 이미지 로드
        card.querySelectorAll('.featured-thumbnail img').forEach((img, index) => {
            loadThumbnailForSong(img, featuredSongs[index]);
        });
        
        // 클릭 이벤트
        card.addEventListener('click', () => {
            showGenreSongs(genre);
        });
        
        // 터치 피드백
        card.addEventListener('touchstart', function() {
            this.style.opacity = '0.8';
        }, { passive: true });
        
        card.addEventListener('touchend', function() {
            this.style.opacity = '1';
        }, { passive: true });
        
        grid.appendChild(card);
    });
}

// 연도별 카드 생성
function createYearCards() {
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid';
    
    const yearGroups = getSongsByYear();
    const sortedYears = Object.keys(yearGroups).sort((a, b) => {
        const yearA = Number(a);
        const yearB = Number(b);
        const hasYearA = Number.isFinite(yearA);
        const hasYearB = Number.isFinite(yearB);
        
        if (hasYearA && hasYearB) return yearB - yearA;
        if (hasYearA) return -1;
        if (hasYearB) return 1;
        return a.localeCompare(b, 'ko');
    });
    
    sortedYears.forEach(year => {
        const songs = yearGroups[year];
        const card = document.createElement('div');
        card.className = 'year-card';
        card.dataset.year = year;
        
        // 대표곡 썸네일 (최대 4개)
        const featuredSongs = songs.slice(0, 4);
        const thumbnailsHtml = featuredSongs.map((song, index) => 
            `<div class="featured-thumbnail" style="z-index: ${4 - index}">
                <img src="" alt="${song.title}" data-youtube-id="${song.youtubeId}">
            </div>`
        ).join('');
        
        card.innerHTML = `
            <div class="artist-thumbnails">
                ${thumbnailsHtml}
            </div>
            <div class="card-info">
                <div class="card-title">${formatYearLabel(year)}</div>
                <div class="card-artist">${songs.length}곡</div>
                <div class="card-description">${songs.map(s => s.artist).filter((v, i, a) => a.indexOf(v) === i).join(', ')}</div>
                <div class="song-count">${songs.length}곡</div>
            </div>
        `;
        
        // 썸네일 이미지 로드
        card.querySelectorAll('.featured-thumbnail img').forEach((img, index) => {
            loadThumbnailForSong(img, featuredSongs[index]);
        });
        
        // 클릭 이벤트
        card.addEventListener('click', () => {
            showYearSongs(year);
        });
        
        // 터치 피드백
        card.addEventListener('touchstart', function() {
            this.style.opacity = '0.8';
        }, { passive: true });
        
        card.addEventListener('touchend', function() {
            this.style.opacity = '1';
        }, { passive: true });
        
        grid.appendChild(card);
    });
}

// 작업 유형별 카드 생성
function createCategoryCards() {
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid category-view';
    
    const categoryGroups = getSongsByCategory();
    // 카테고리 순서 정의: Digital Editing, Mixing, Broadcasting, Recording
    const categoryOrder = ['Digital Editing', 'Mixing', 'Broadcasting', 'Recording'];
    const sortedCategories = Object.keys(categoryGroups).sort((a, b) => {
        const indexA = categoryOrder.indexOf(a);
        const indexB = categoryOrder.indexOf(b);
        if (indexA === -1 && indexB === -1) return a.localeCompare(b);
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
        return indexA - indexB;
    });
    
    sortedCategories.forEach(category => {
        const songs = categoryGroups[category];
        const card = document.createElement('div');
        card.className = 'category-card';
        card.dataset.category = category;
        
        // 카테고리 전용 분할 썸네일 (최대 3x3)
        const layout = getCategoryThumbnailLayout(songs.length);
        const cellCount = Math.min(layout.cols * layout.rows, 9);
        const thumbnailSongs = getCategoryThumbnailSongs(songs, cellCount);
        const thumbnailsHtml = thumbnailSongs.map(song => 
            `<div class="category-thumbnail">
                <img src="" alt="${song.title}" data-youtube-id="${song.youtubeId}">
            </div>`
        ).join('');
        
        card.innerHTML = `
            <div class="artist-thumbnails category-thumbnails-grid" style="--thumb-cols: ${layout.cols}; --thumb-rows: ${layout.rows};">
                ${thumbnailsHtml}
            </div>
            <div class="card-info">
                <div class="card-title">${category}</div>
                <div class="card-artist">${songs.length}곡</div>
                <div class="card-description">${songs.map(s => s.artist).filter((v, i, a) => a.indexOf(v) === i).join(', ')}</div>
                <div class="song-count">${songs.length}곡</div>
            </div>
        `;
        
        // 썸네일 이미지 로드
        card.querySelectorAll('.category-thumbnail img').forEach((img, index) => {
            loadThumbnailForSong(img, thumbnailSongs[index]);
        });
        
        // 클릭 이벤트
        card.addEventListener('click', () => {
            showCategorySongs(category);
        });
        
        // 터치 피드백
        card.addEventListener('touchstart', function() {
            this.style.opacity = '0.8';
        }, { passive: true });
        
        card.addEventListener('touchend', function() {
            this.style.opacity = '1';
        }, { passive: true });
        
        grid.appendChild(card);
    });
}

// 장르별 노래 목록 표시
function showGenreSongs(genre) {
    const genreGroups = getSongsByGenre();
    const songs = genreGroups[genre] || [];
    
    currentView = 'songs';
    currentArtist = genre;
    updateViewIntro(`${genre} 작업물`, `${songs.length}곡을 연속으로 확인할 수 있습니다.`);
    updateHeaderMeta(`장르: ${genre}`);
    
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid songs-view';
    
    // 뒤로가기 버튼
    const backButton = document.createElement('button');
    backButton.className = 'back-button';
    backButton.innerHTML = '← 장르 목록으로';
    backButton.addEventListener('click', () => {
        currentView = 'artists';
        currentArtist = null;
        createCardsByFilter('genre');
    });
    grid.appendChild(backButton);
    
    // 장르 헤더
    const genreHeader = document.createElement('div');
    genreHeader.className = 'artist-header';
    genreHeader.innerHTML = `
        <h2>${genre}</h2>
        <p>${songs.length}곡</p>
    `;
    grid.appendChild(genreHeader);
    
    // 노래 카드 생성
    songs.forEach(song => {
        const card = createSongCard(song);
        grid.appendChild(card);
    });
}

// 연도별 노래 목록 표시
function showYearSongs(year) {
    const yearGroups = getSongsByYear();
    const songs = yearGroups[year] || [];
    
    currentView = 'songs';
    currentArtist = year;
    updateViewIntro(`${formatYearLabel(year)} 작업물`, `${songs.length}곡을 연도 기준으로 정리했습니다.`);
    updateHeaderMeta(`연도: ${year}`);
    
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid songs-view';
    
    // 뒤로가기 버튼
    const backButton = document.createElement('button');
    backButton.className = 'back-button';
    backButton.innerHTML = '← 연도 목록으로';
    backButton.addEventListener('click', () => {
        currentView = 'artists';
        currentArtist = null;
        createCardsByFilter('year');
    });
    grid.appendChild(backButton);
    
    // 연도 헤더
    const yearHeader = document.createElement('div');
    yearHeader.className = 'artist-header';
    yearHeader.innerHTML = `
        <h2>${formatYearLabel(year)}</h2>
        <p>${songs.length}곡</p>
    `;
    grid.appendChild(yearHeader);
    
    // 노래 카드 생성
    songs.forEach(song => {
        const card = createSongCard(song);
        grid.appendChild(card);
    });
}

// 작업 유형별 노래 목록 표시
function showCategorySongs(category) {
    const categoryGroups = getSongsByCategory();
    const songs = categoryGroups[category] || [];
    
    currentView = 'songs';
    currentArtist = category;
    updateViewIntro(`${category} 작업물`, `${songs.length}곡을 작업 유형 기준으로 보여줍니다.`);
    updateHeaderMeta(`작업유형: ${category}`);
    
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid songs-view';
    
    // 뒤로가기 버튼
    const backButton = document.createElement('button');
    backButton.className = 'back-button';
    backButton.innerHTML = '← 작업유형 목록으로';
    backButton.addEventListener('click', () => {
        currentView = 'artists';
        currentArtist = null;
        createCardsByFilter('category');
    });
    grid.appendChild(backButton);
    
    // 작업 유형 헤더
    const categoryHeader = document.createElement('div');
    categoryHeader.className = 'artist-header';
    categoryHeader.innerHTML = `
        <h2>${category}</h2>
        <p>${songs.length}곡</p>
    `;
    grid.appendChild(categoryHeader);
    
    // 노래 카드 생성
    songs.forEach(song => {
        const card = createSongCard(song);
        grid.appendChild(card);
    });
}

// 노래 카드 생성 헬퍼 함수
function createSongCard(song) {
    const card = document.createElement('div');
    card.className = 'music-card';
    card.dataset.musicId = song.id;
    
    card.innerHTML = `
        <div class="card-thumbnail">
            <img src="" alt="${song.title}" data-youtube-id="${song.youtubeId}">
        </div>
        <div class="card-info">
            <div class="card-title">${song.title}</div>
            <div class="card-artist">${song.artist}</div>
            <span class="card-genre">${song.genre}</span>
        </div>
    `;
    
    // 썸네일 이미지 로드
    const thumbnailImg = card.querySelector('.card-thumbnail img');
    loadThumbnailForSong(thumbnailImg, song);
    
    // 클릭 이벤트
    card.addEventListener('click', (e) => {
        e.preventDefault();
        openModal({ ...song, artist: song.artist });
    });
    
    // 터치 피드백
    card.addEventListener('touchstart', function() {
        this.style.opacity = '0.8';
    }, { passive: true });
    
    card.addEventListener('touchend', function() {
        this.style.opacity = '1';
    }, { passive: true });
    
    return card;
}

// 아티스트의 노래 목록 표시
function showArtistSongs(artistName) {
    const artist = artistsData[artistName];
    if (!artist) return;
    
    currentView = 'songs';
    currentArtist = artistName;
    updateViewIntro(`${artist.name} 작업물`, `${artist.songs.length}곡을 아티스트 기준으로 확인합니다.`);
    updateHeaderMeta(`아티스트: ${artist.name}`);
    
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';
    grid.className = 'portfolio-grid songs-view';
    
    // 뒤로가기 버튼 추가
    const backButton = document.createElement('button');
    backButton.className = 'back-button';
    const backText = currentFilter === 'artist' ? '← 아티스트 목록으로' : 
                     currentFilter === 'genre' ? '← 장르 목록으로' : 
                     currentFilter === 'year' ? '← 연도 목록으로' :
                     currentFilter === 'category' ? '← 작업유형 목록으로' :
                     '← 목록으로';
    backButton.innerHTML = backText;
    backButton.addEventListener('click', () => {
        currentView = 'artists';
        currentArtist = null;
        createCardsByFilter(currentFilter);
    });
    grid.appendChild(backButton);
    
    // 아티스트 헤더
    const artistHeader = document.createElement('div');
    artistHeader.className = 'artist-header';
    artistHeader.innerHTML = `
        <h2>${artist.name}</h2>
        <p>${artist.description}</p>
    `;
    grid.appendChild(artistHeader);
    
    // 노래 카드 생성
    artist.songs.forEach(song => {
        const card = createSongCard({ ...song, artist: artist.name });
        grid.appendChild(card);
    });
}

// 호버 시 정보 표시 (간단한 툴팁 스타일)
let hoverTimeout;
function showMusicInfo(music) {
    hoverTimeout = setTimeout(() => {
        // 호버 시 추가 정보를 표시할 수 있습니다
        // 현재는 클릭 시 모달로 표시됩니다
    }, 500);
}

function hideMusicInfo() {
    clearTimeout(hoverTimeout);
}

// 모달 열기
function openModal(music) {
    const modal = document.getElementById('musicModal');
    const modalBody = document.getElementById('modalBody');
    const youtubeWatchUrl = `https://www.youtube.com/watch?v=${music.youtubeId}`;
    const isMobile = window.innerWidth <= 768;
    const isFileProtocol = window.location.protocol === 'file:';
    const youtubeParams = new URLSearchParams({
        autoplay: '0',
        rel: '0',
        playsinline: isMobile ? '1' : '0'
    });
    if (!isFileProtocol) {
        youtubeParams.set('origin', window.location.origin);
    }

    const youtubeBlock = `
        <div class="youtube-embed">
            <iframe
                src="https://www.youtube-nocookie.com/embed/${music.youtubeId}?${youtubeParams.toString()}"
                title="${music.title} - ${music.artist}"
                referrerpolicy="strict-origin-when-cross-origin"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen
                loading="lazy">
            </iframe>
        </div>
        ${isFileProtocol ? `<div class="youtube-fallback"><p class="youtube-fallback-message">현재 file://로 열려 있어 재생 오류가 날 수 있습니다. 브라우저에서 http://127.0.0.1:8000 으로 접속하면 페이지 내 재생이 됩니다. <a class="youtube-open-link" href="${youtubeWatchUrl}" target="_blank" rel="noopener noreferrer">YouTube에서 직접 보기</a></p></div>` : ''}
    `;
    
    modalBody.innerHTML = `
        <h2 class="modal-title">${music.title}</h2>
        <div class="modal-artist">${music.artist}</div>
        <p class="modal-description">${music.description}</p>
        <div class="modal-details">
            <div class="detail-item">
                <div class="detail-label">작업유형</div>
                <div class="detail-value">${music.workDisplay || music.genre}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">연도</div>
                <div class="detail-value">${music.year}</div>
            </div>
        </div>
        ${youtubeBlock}
    `;
    
    modal.classList.add('show');
    
    // 모바일에서 스크롤 방지
    if (window.innerWidth <= 768) {
        document.body.style.overflow = 'hidden';
    }
}

// 모달 닫기
function closeModal() {
    const modal = document.getElementById('musicModal');
    modal.classList.remove('show');
    
    // 모바일에서 스크롤 복원
    document.body.style.overflow = '';
    
    // YouTube 비디오 정지 (모달 닫을 때)
    const iframe = modal.querySelector('iframe');
    if (iframe) {
        iframe.src = iframe.src; // iframe 리로드하여 비디오 정지
    }
}

// 필터 탭 클릭 이벤트
function setupFilterTabs() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const filterMode = tab.dataset.filter;
            
            // 활성 탭 업데이트
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // 필터 모드 변경
            currentFilter = filterMode;
            currentView = 'artists';
            currentArtist = null;
            
            // 카드 재생성
            createCardsByFilter(filterMode);
        });
    });
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', async () => {
    await loadPortfolioDataFromCsv();
    createCardsByFilter('category');
    setupFilterTabs();
    
    // 모달 닫기 버튼
    document.getElementById('closeModal').addEventListener('click', closeModal);
    
    // 모달 배경 클릭 시 닫기
    document.getElementById('musicModal').addEventListener('click', (e) => {
        if (e.target.id === 'musicModal') {
            closeModal();
        }
    });
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (currentView === 'songs') {
                currentView = 'artists';
                currentArtist = null;
                createCardsByFilter(currentFilter);
            } else {
                closeModal();
            }
        }
    });
});
