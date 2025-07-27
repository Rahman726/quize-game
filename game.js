document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreDisplay = document.getElementById('score');
    const startBtn = document.getElementById('startBtn');
    const gameOverDisplay = document.getElementById('gameOver');
    
    const gridSize = 20;
    const tileCount = canvas.width / gridSize;
    
    let snake = [];
    let food = {};
    let score = 0;
    let xVelocity = 0;
    let yVelocity = 0;
    let gameRunning = false;
    let gameLoop;
    
    // Initialize game
    function initGame() {
        snake = [
            {x: 10, y: 10}
        ];
        food = {
            x: Math.floor(Math.random() * tileCount),
            y: Math.floor(Math.random() * tileCount)
        };
        score = 0;
        xVelocity = 0;
        yVelocity = 0;
        scoreDisplay.textContent = score;
        gameOverDisplay.classList.add('hidden');
        gameRunning = true;
    }
    
    // Draw game elements
    function drawGame() {
        // Clear canvas
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw snake
        ctx.fillStyle = 'green';
        snake.forEach(segment => {
            ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize - 2, gridSize - 2);
        });
        
        // Draw food
        ctx.fillStyle = 'red';
        ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);
    }
    
    // Update game state
    function updateGame() {
        // Move snake
        const head = {x: snake[0].x + xVelocity, y: snake[0].y + yVelocity};
        snake.unshift(head);
        
        // Check if snake ate food
        if (head.x === food.x && head.y === food.y) {
            score++;
            scoreDisplay.textContent = score;
            food = {
                x: Math.floor(Math.random() * tileCount),
                y: Math.floor(Math.random() * tileCount)
            };
        } else {
            snake.pop();
        }
        
        // Check collision with walls
        if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
            gameOver();
            return;
        }
        
        // Check collision with self
        for (let i = 1; i < snake.length; i++) {
            if (head.x === snake[i].x && head.y === snake[i].y) {
                gameOver();
                return;
            }
        }
    }
    
    // Game over
    function gameOver() {
        gameRunning = false;
        clearInterval(gameLoop);
        gameOverDisplay.classList.remove('hidden');
    }
    
    // Main game loop
    function game() {
        updateGame();
        drawGame();
    }
    
    // Start game
    startBtn.addEventListener('click', () => {
        initGame();
        gameLoop = setInterval(game, 100);
    });
    
    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        if (!gameRunning) return;
        
        // Prevent reverse direction
        switch(e.key) {
            case 'ArrowUp':
                if (yVelocity !== 1) {
                    xVelocity = 0;
                    yVelocity = -1;
                }
                break;
            case 'ArrowDown':
                if (yVelocity !== -1) {
                    xVelocity = 0;
                    yVelocity = 1;
                }
                break;
            case 'ArrowLeft':
                if (xVelocity !== 1) {
                    xVelocity = -1;
                    yVelocity = 0;
                }
                break;
            case 'ArrowRight':
                if (xVelocity !== -1) {
                    xVelocity = 1;
                    yVelocity = 0;
                }
                break;
        }
    });
});