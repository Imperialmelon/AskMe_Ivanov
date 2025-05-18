function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const setupQuestionLikes = () => {
    const questionCards = document.querySelectorAll('[data-question-id]');
    
    questionCards.forEach(card => {
        const likeButton = card.querySelector('.like-button');
        const likeCount = card.querySelector('.like-count');
        const questionId = card.dataset.questionId;
        const csrfToken = getCookie('csrftoken');

        const initialIsLiked = card.dataset.isLiked === 'True';
        console.log(`Question ${questionId} - isLiked: ${initialIsLiked}`);
        
        if (initialIsLiked) {
            likeButton.classList.add('active');
        }
        likeButton.addEventListener('click', () => {
            fetch(`/question_like/${questionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                }
            })
            .then(response => {
                if (response.status === 401) {
                    window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
                    return Promise.reject('Unauthorized');
                }
                return response.json();
            })
            .then(data => {
                likeCount.textContent = data.question_likes_count;
                likeButton.classList.toggle('active', data.is_liked);
                
                card.dataset.isLiked = data.is_liked ? 'True' : 'False';
            })
            .catch(error => console.error('Error:', error));
        });
    });
};


const setupAnswerLikes = () => {
    const answerCards = document.querySelectorAll('[data-answer-id]');
    
    answerCards.forEach(card => {
        const likeButton = card.querySelector('.answer-like-button');
        const likeCount = card.querySelector('.answer-like-count');
        const answerId = card.dataset.answerId;
        const csrfToken = getCookie('csrftoken');

        const initialIsLiked = card.dataset.isLiked === 'True';
        console.log(`Answer ${answerId} - isLiked: ${initialIsLiked}`);
        
        if (initialIsLiked) {
            likeButton.classList.add('active');
        }


        likeButton.addEventListener('click', () => {
            fetch(`/answer_like/${answerId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                }
            })
            .then(response => {
                if (response.status === 401) {
                    window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
                    return Promise.reject('Unauthorized');
                }
                return response.json();
            })
            .then(data => {
                likeCount.textContent = data.answer_likes_count;
                likeButton.classList.toggle('active', data.is_liked);
                card.dataset.isLiked = data.is_liked ? 'True' : 'False';
            })
            .catch(error => console.error('Error:', error));
            console.log(1)
        });
    });
};

const setupUsefulAnswers = () => {
    const answerCards = document.querySelectorAll('[data-answer-id]');
    const csrfToken = getCookie('csrftoken');
    
    answerCards.forEach(card => {
        const checkbox = card.querySelector('.helpful-checkbox');
        const answerId = card.dataset.answerId;
        
        const questionCard = document.querySelector('.question-card');
        const isAuthor = questionCard && questionCard.dataset.isAuthor === 'True';
        
        if (!isAuthor) {
            checkbox.disabled = true;
        } else {
            checkbox.addEventListener('change', () => {
                fetch(`/set_useful/${answerId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    }
                })
                .then(response => {
                    if (response.status === 401) {
                        window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
                        return Promise.reject('Unauthorized');
                    }
                    return response.json();
                })
                .then(data => {
                    checkbox.checked = data.is_useful;
                    

                    card.dataset.isHelpful = data.is_useful ? 'True' : 'False';
                    
                    if (data.is_useful) {
                        card.classList.add('useful-answer');
                    } else {
                        card.classList.remove('useful-answer');
                    }
                })
            });
        }
    });
};




document.addEventListener('DOMContentLoaded', setupQuestionLikes);
document.addEventListener('DOMContentLoaded', setupAnswerLikes);
document.addEventListener('DOMContentLoaded', setupUsefulAnswers);