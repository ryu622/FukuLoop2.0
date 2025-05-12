window.onload = function() {
    fetch(`/api/counts`)
        .then(response => {
            // レスポンスが成功かどうかを確認
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();}
        )
    .then(data => {
        console.log(data);
        //各値を変数に代入
        const labels=Object.keys(data.data);
        const values=Object.values(data.data);
        console.log(labels);
        console.log(values);
            
         const ctx = document.getElementById('myChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '完了数',
                        data: values,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
    
    
};