$(document).ready(function() {
    $("#city").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: autocompleteUrl,
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 2,
    });

    // Извлечение данных для графика
    var labels = weatherDataTimes.map(time => new Date(time).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit", hour12: false }));

    var temperatures = weatherDataTemperatures;

    // Подготовка данных для графика
    var data = {
        labels: labels,
        datasets: [{
            label: 'Temperature',
            backgroundColor: 'rgb(54, 162, 235)',
            borderColor: 'rgb(54, 162, 235)',
            data: temperatures,
            fill: false,
        }]
    };

    // Создание графика
    var ctx = document.getElementById('weatherChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Hourly Temperature Forecast'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                }
            }
        }
    });
});
