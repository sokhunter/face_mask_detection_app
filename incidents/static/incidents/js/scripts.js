colors = {
    yellow: '#FCD34D',
    red: '#EF4444',
    blue: '#6366F1',
    green: '#34D399'
}

$(function () {
    var $chart = $("#incidents-chart");
    $.ajax({
        url: $chart.data("url"),
        success: function (data) {
            var maxIncidents = data.max_incidents
            var data1 = []
            var data2 = []
            for (let index = 0; index < data.data.length; index++) {
                const e = data.data[index];
                if (e > 2) {
                    data1.push(maxIncidents)
                    data2.push(e - maxIncidents)
                } else {
                    data1.push(e)
                    data2.push(0)
                }
            }
            var ctx = $chart[0].getContext("2d");
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Incidents',
                        backgroundColor: "#4338CA",
                        data: data1
                    }, {
                        label: 'Danger',
                        backgroundColor: "#EF4444",
                        data: data2,
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false
                        },
                        annotation: {
                            annotations: {
                                line1: {
                                    type: 'line',
                                    yMin: maxIncidents,
                                    yMax: maxIncidents,
                                    borderColor: '#EF4444',
                                    borderWidth: 3,
                                }
                            }
                        }
                    },
                    responsive: true,
                    legend: {
                        display: false,
                    },
                    scales: {
                        y: {
                            stacked: true,
                            beginAtZero: true,
                        },
                        x: {
                            stacked: true,
                        }
                    }
                }
            });
        }
    });

    var $chart2 = $("#incidents-by-worker-chart");
    $.ajax({
        url: $chart2.data("url"),
        success: function (data) {
            var maxIncidents = data.max_incidents
            var data1 = []
            var data2 = []
            for (let index = 0; index < data.data.length; index++) {
                const e = data.data[index];
                if (e > 2) {
                    data1.push(maxIncidents)
                    data2.push(e - maxIncidents)
                } else {
                    data1.push(e)
                    data2.push(0)
                }
            }
            var ctx = $chart2[0].getContext("2d");
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Incidents',
                        backgroundColor: "#4338CA",
                        data: data1
                    }, {
                        label: 'Danger',
                        backgroundColor: "#EF4444",
                        data: data2,
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false
                        },
                        annotation: {
                            annotations: {
                                line1: {
                                    type: 'line',
                                    yMin: maxIncidents,
                                    yMax: maxIncidents,
                                    borderColor: '#EF4444',
                                    borderWidth: 3,
                                }
                            }
                        }
                    },
                    responsive: true,
                    legend: {
                        display: false,
                    },
                    scales: {
                        y: {
                            stacked: true,
                            beginAtZero: true,
                        },
                        x: {
                            stacked: true,
                        }
                    },
                }
            });
        }
    });

    var $chart3 = $("#incidents-by-category-bar-chart");
    $.ajax({
        url: $chart3.data("url"),
        success: function (data) {
            var ctx = $chart3[0].getContext("2d");
            var datasets = []

            for (let i = 0; i < data.data.length; ++i) {
                datasets.push({
                    label: data.data_labels[i],
                    backgroundColor: colors[data.data_colors[i]],
                    data: data.data[i]
                });
            }

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    legend: {
                        display: true,
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    });

    var $chart3_2 = $("#incidents-by-category-bar-chart-2");
    $.ajax({
        url: $chart3_2.data("url"),
        success: function (data) {
            var ctx = $chart3_2[0].getContext("2d");
            var datasets = []

            for (let i = 0; i < data.data.length; ++i) {
                datasets.push({
                    label: data.data_labels[i],
                    backgroundColor: colors[data.data_colors[i]],
                    data: data.data[i]
                });
            }

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    legend: {
                        display: true,
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    });

    var $chart4 = $("#incidents-by-category-doughnut-chart");
    $.ajax({
        url: $chart4.data("url"),
        success: function (data) {
            var ctx = $chart4[0].getContext("2d");
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Incidents',
                        backgroundColor: data.data_colors.map(e => colors[e]),
                        data: data.data,
                    }]
                },
                options: {
                    aspectRatio: 2,
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    },
                }
            });
        }
    });

    var $summary = $("#incidents-summary-charts");
    $.ajax({
        url: $summary.data("url"),
        success: function (data) {
            Object.keys(data.summary).forEach(e => {
                var ctx = document.getElementById(e + '-incidents-chart').getContext('2d');
                var count = document.getElementById(e + '-count');
                var increment = document.getElementById(e + '-increment');

                count.innerHTML = data.summary[e].count

                var change = data.summary[e].change

                if (change > 0) {
                    increment.classList.add("text-red-500");
                    increment.innerHTML = '+' + change + '%'
                } else if (change < 0) {
                    increment.classList.add("text-green-500");
                    increment.innerHTML = '-' + -change + '%'
                } else {
                    increment.classList.add("text-500");
                    increment.innerHTML = '+' + change + '%'
                }

                var datasets = []

                for (let i = 0; i < data.data_labels.length; ++i) {
                    datasets.push({
                        label: data.data_labels[i],
                        backgroundColor: colors[data.data_colors[i]],
                        data: [data.summary[e].data[i]]
                    });
                }

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: datasets
                    },
                    plugins: [ChartDataLabels],
                    // plugins: {
                    //     [ChartDataLabels]: {
                    //         display: function (context) {
                    //             return context.dataset.data[context.dataIndex] > 0;
                    //         },
                    //         color: "white"
                    //     },
                    // },
                    options: {
                        borderRadius: 5,
                        aspectRatio: 6,
                        indexAxis: 'y',
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                enabled: false,
                            }
                        },
                        scales: {
                            x: {
                                display: false,
                                stacked: true,
                                grid: {
                                    display: false
                                },
                            },
                            y: {
                                display: false,
                                stacked: true,
                                beginAtZero: true,
                                grid: {
                                    display: false
                                },
                            }
                        }
                    }
                });
            })
        }
    });
});