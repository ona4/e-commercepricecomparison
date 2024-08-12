document.addEventListener('DOMContentLoaded', function() {
    const compareList = document.getElementById('compareList');
    const compareButton = document.getElementById('compareButton');
    const comparisonModal = document.getElementById('comparisonModal');
    const closeModalBtn = comparisonModal.querySelector('.close');
    const comparisonResultContainer = document.getElementById('comparisonResult');
    let productsToCompare = [];

    document.querySelectorAll('.stars').forEach(starSpan => {
        const rating = parseFloat(starSpan.dataset.rating);
        //starSpan.innerHTML ='asd:'
        starSpan.innerHTML = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    });

    document.querySelectorAll('.add-to-compare').forEach(button => {
        button.addEventListener('click', function() {
                if (productsToCompare.length >= 1) {
            alert("You can only add one item. Please remove an item by clicking the trash icon");


            return;
        }
            const productCard = this.closest('.result-card');
            const productId = productCard.dataset.id;
            const productTitle = productCard.querySelector('h3').textContent;

            if (!productsToCompare.includes(productId)) {
                productsToCompare.push(productId);

                const listItem = document.createElement('div');
                listItem.textContent = productTitle;
                compareList.appendChild(listItem);

                compareButton.style.display = 'block';
            }
        });
    });

    closeModalBtn.addEventListener('click', function() {
        comparisonModal.style.display = 'none';
    });

    compareButton.addEventListener('click', function() {
        comparisonModal.style.display = 'block';
        const selectedProducts = productsToCompare.map(productId => {
            const productCard = document.querySelector(`.result-card[data-id="${productId}"]`);
            const priceText = productCard.querySelector('.price').textContent;
            const price = parseFloat(priceText.replace(/[^0-9.-]+/g, ''));
            const url = productCard.querySelector('.site a') ? productCard.querySelector('.site a').href : '';

            return {
                title: productCard.querySelector('h3').textContent,
                price: price,
                url: url,
            };
        });

        if (selectedProducts.length > 0) {
            const prices = selectedProducts.map(product => product.price);
            const lowestPrice = Math.min(...prices);
            const averagePrice = (prices.reduce((sum, price) => sum + price, 0) / prices.length).toFixed(2);
            const recommendedPrice = lowestPrice;

            comparisonResultContainer.innerHTML = `
                <p><strong>Lowest Price:</strong> $${lowestPrice.toFixed(2)}</p>
                <p><strong>Average Price:</strong> $${averagePrice}</p>
                <p><strong>Recommended Price:</strong> $${recommendedPrice.toFixed(2)}</p>
                <div id="sadeceyazi">Overall ratings:</div>
                <div id="sentimentAnalysis">result:</div>
                ${selectedProducts.map(product => `
                    <p>
                        <a>${product.title}${product.url}</a> - $${product.price.toFixed(2)}
                        <button class="remove-from-comparison" data-id="${product.title}">🗑️</button>
                    </p>
                `).join('')}
            `;

            comparisonResultContainer.addEventListener('click', function(event) {
                if (event.target.classList.contains('remove-from-comparison')) {
                    const productTitle = event.target.dataset.id;
                    removeProductFromComparison(productTitle);
                }
            });

            analyzeSentiment(selectedProducts.map(product => product.title));
        } else {
            comparisonResultContainer.innerHTML = '<p>No products selected for review.</p>';
        }
    });

    function removeProductFromComparison(productTitle) {
        productsToCompare = productsToCompare.filter(productId => {
            const productCard = document.querySelector(`.result-card[data-id="${productId}"]`);
            return productCard.querySelector('h3').textContent !== productTitle;
        });

        const listItems = compareList.querySelectorAll('div');
        listItems.forEach(item => {
            if (item.textContent === productTitle) {
                item.remove();
            }
        });

        compareButton.click();

        if (productsToCompare.length === 0) {
            compareButton.style.display = 'none';
        }
    }

    window.addEventListener('click', function(event) {
        if (event.target === comparisonModal) {
            comparisonModal.style.display = 'none';
        }
    });

    async function analyzeSentiment(titles) {
        try {
            const response = await fetch('/analyze_sentiment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ titles: titles }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            document.getElementById('sentimentAnalysis').textContent = data.overall_sentiment;
        } catch (error) {
            console.error('Error analyzing sentiment:', error);
            document.getElementById('sentimentAnalysis').textContent = 'Analysis failed';
        }
    }
});
