window.onload = function() {
    var searchform = document.getElementById('searchform');
    searchform.addEventListener('submit', function(event) {
        event.preventDefault();
        document.getElementById('container').innerHTML = '<canvas id="canvas"></canvas>';
        var project = searchform.project.value;
        var datefrom = searchform.datefrom.value;
        var dateto = searchform.dateto.value;
        var interval = searchform.interval.value;

        api_url = "http://127.0.0.1:8000/api/pull-request-datasets?project=" + project + "&datefrom=" + datefrom + "&dateto=" + dateto + "&interval=" + interval;

        var response = $.ajax(api_url).done(function() {
            var labels = response.responseJSON.labels;
            //var pr_amounts_dataset = response.responseJSON.pr_amounts;
            var merged_pr_amounts_dataset = response.responseJSON.merged_pr_amounts;
            //var not_merged_pr_amounts_dataset = response.responseJSON.not_merged_pr_amounts;
            var conflicting_pr_amounts_dataset = response.responseJSON.conflicting_pr_amounts;
            var pairwise_conflict_amounts_dataset = response.responseJSON.pairwise_conflict_amounts;
            var real_conflict_amounts_dataset = response.responseJSON.real_conflict_amounts;
            var pull_request_groups_amounts_dataset = response.responseJSON.pull_request_groups_amounts;
            var pull_request_groups_by_datasets = response.responseJSON.pull_request_groups_by_datasets;

            var color = Chart.helpers.color;

            var barChartData = {
                labels: labels,
                datasets: [{
                        label: '#PR Merged',
                        stack: 'Stack 0',
                        backgroundColor: color(window.chartColors.green).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.green,
                        borderWidth: 1,
                        data: merged_pr_amounts_dataset
                    },
                    /*{
                                       label: '#PR Rejected',
                                       stack: 'Stack 0',
                                       backgroundColor: color(window.chartColors.grey).alpha(0.5).rgbString(),
                                       borderColor: window.chartColors.grey,
                                       borderWidth: 1,
                                       data: not_merged_pr_amounts_dataset
                                   },*/
                    {
                        label: '#PR With Conflicts',
                        stack: 'Stack 1',
                        backgroundColor: color(window.chartColors.yellow).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.yellow,
                        borderWidth: 1,
                        data: conflicting_pr_amounts_dataset
                    }, {
                        label: '#Pairwise Conflicts',
                        stack: 'Stack 2',
                        backgroundColor: color(window.chartColors.orange).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.orange,
                        borderWidth: 1,
                        data: pairwise_conflict_amounts_dataset
                    },
                    /*{
                                           label: '#Historical PR Conflicts',
                                           stack: 'Stack 3',
                                           backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
                                           borderColor: window.chartColors.red,
                                           borderWidth: 1,
                                           data: real_conflict_amounts_dataset
                                       },*/
                    {
                        label: '#PR Groups',
                        stack: 'Stack 4',
                        backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.blue,
                        borderWidth: 1,
                        data: pull_request_groups_amounts_dataset
                    }
                ]

            };

            var colorNames = Object.keys(window.chartColors);

            pull_request_groups_by_datasets.forEach(function(pull_request_groups_by_dataset, index) {
                console.log(index);
                var colorName = colorNames[index % colorNames.length];
                var dsColor = window.chartColors[colorName];
                var new_dataset = [{
                    label: 'Group ' + String(index + 1),
                    stack: 'Stack 5',
                    backgroundColor: color(dsColor).alpha(0.5).rgbString(),
                    borderColor: dsColor,
                    borderWidth: 1,
                    data: pull_request_groups_by_dataset
                }]

                barChartData.datasets = barChartData.datasets.concat(new_dataset);
            });

            var ctx = document.getElementById('canvas').getContext('2d');
            window.myBar = new Chart(ctx, {
                type: 'bar',
                data: barChartData,
                options: {
                    responsive: true,
                    scales: {
                        xAxes: [{
                            stacked: true,
                        }],
                        yAxes: [{
                            stacked: true
                        }]
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Pull Request Analysis'
                        }
                    }
                }
            });
        });
    });
};



// window.onload = function() {
//     var ctx = document.getElementById('canvas').getContext('2d');
//     window.myBar = new Chart(ctx, {
//         type: 'bar',
//         data: barChartData,
//         options: {
//             responsive: true,
//             plugins: {
//                 legend: {
//                     position: 'top',
//                 },
//                 title: {
//                     display: true,
//                     text: 'Chart.js Bar Chart'
//                 }
//             }
//         }
//     });

// };

// var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];



// document.getElementById('randomizeData').addEventListener('click', function() {
//     var zero = Math.random() < 0.2 ? true : false;
//     barChartData.datasets.forEach(function(dataset) {
//         dataset.data = dataset.data.map(function() {
//             return zero ? 0.0 : randomScalingFactor();
//         });

//     });
//     window.myBar.update();
// });

// var colorNames = Object.keys(window.chartColors);
// document.getElementById('addDataset').addEventListener('click', function() {
//     var colorName = colorNames[barChartData.datasets.length % colorNames.length];
//     var dsColor = window.chartColors[colorName];
//     var newDataset = {
//         label: 'Dataset ' + (barChartData.datasets.length + 1),
//         backgroundColor: color(dsColor).alpha(0.5).rgbString(),
//         borderColor: dsColor,
//         borderWidth: 1,
//         data: []
//     };

//     for (var index = 0; index < barChartData.labels.length; ++index) {
//         newDataset.data.push(randomScalingFactor());
//     }

//     barChartData.datasets.push(newDataset);
//     window.myBar.update();
// });

// document.getElementById('addData').addEventListener('click', function() {
//     if (barChartData.datasets.length > 0) {
//         var month = MONTHS[barChartData.labels.length % MONTHS.length];
//         barChartData.labels.push(month);

//         for (var index = 0; index < barChartData.datasets.length; ++index) {
//             barChartData.datasets[index].data.push(randomScalingFactor());
//         }

//         window.myBar.update();
//     }
// });

// document.getElementById('removeDataset').addEventListener('click', function() {
//     barChartData.datasets.pop();
//     window.myBar.update();
// });

// document.getElementById('removeData').addEventListener('click', function() {
//     barChartData.labels.splice(-1, 1); // remove the label first

//     barChartData.datasets.forEach(function(dataset) {
//         dataset.data.pop();
//     });

//     window.myBar.update();
// });