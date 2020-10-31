const content_loading = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>`;
const port_item = (id) => `<a class="list-group-item list-group-item-action port-list-item" data-toggle="list" href="#" role="tab" aria-controls="home">${id}</a>`;
const room_card = (roomId) => `
<div class="card-body room-card" id="room-card-${roomId}">
    <img class="card-img-top" src="/static/img/rooms/${roomId}.jpg" alt="Card image cap">

    <!-- Title -->
    <h4 class="card-title">${roomId}</h4>
    <!-- Text -->
    <p class="card-text"></p>
    
    <!-- Query Table -->
    <div class="query_table" style="display: none;">
        <div class="md-form mx-5 my-5">
          <input placeholder="Date and Time" room-id="${roomId}" type="text" data-open="picker2" class="start-dt form-control date-time picker-opener">
        </div>
        
        <table class="table">
          <thead>
            <tr>
              <th scope="col">Timestamp</th>
              <th scope="col">Sensor</th>
              <th scope="col">Value</th>
            </tr>
          </thead>
          <tbody>
          </tbody>
        </table>
        
        <a class="btn btn-primary btn-run-query disabled" room-id="${roomId}">Query</a>
        <a class="btn btn-primary btn-close-query" room-id="${roomId}">Close</a>
    </div>
    
    <!-- Button -->
    <a class="btn btn-primary btn-start-query" room-id="${roomId}">Query</a>
</div>
`;
const queryTableItem = (sensorId, value, ts) => `
<tr>
   <td>${new Date(ts)}</td>
   <td>${sensorId}</td>
   <td>${value}</td> 
</tr>
`;

const ajax = {
    get: async (url) => $.ajax(url, {
        type: `GET`
    }),

    post: async (url, data) => $.ajax(url, {
        type: `POST`,
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    })
};

const formatDateTime = (ts) => {
    return ("00" + (ts.getMonth() + 1)).slice(-2) + "/" +
        ("00" + ts.getDate()).slice(-2) + "/" +
        ts.getFullYear() + " " +
        ("00" + ts.getHours()).slice(-2) + ":" +
        ("00" + ts.getMinutes()).slice(-2) + ":" +
        ("00" + ts.getSeconds()).slice(-2);
};

const hideEveryThing = () => {
    // hide everything
    $(`#region-loading`).hide();
    $(`#card-select-port`).hide();
    $(`#room-cards-container`).hide();
};

const init = async () => {
    try {
        hideEveryThing();

        // initialize
        console.log(`Init`);

        $(`#region-loading`).show();

        const status = await ajax.get(`/status`);

        if (status && status.serial_working) {
            proceedToDashboard();
            return;
        } else {
            $(`#region-loading`).hide();
        }

        $(`#card-select-port`).show();

        const portList = await ajax.get(`/serial_list`);

        if (portList && portList.ports) {
            $(`#btn-select-port`).removeClass(`disabled`).html(`Select`);

            let listContent = ``;
            for (let i = 0; i < portList.ports.length; i++) {
                listContent += port_item(portList.ports[i]);
            }
            $(`#port-list`).html(listContent);
        } else {
            throw `API "/serial_list" error.`
        }

        $(`#btn-select-port`).click(async (event) => {
            const selectedItem = $(`.port-list-item.active`);

            if (!selectedItem || selectedItem.length == 0) return;
            const selectedPort = selectedItem.html();

            $(`#btn-select-port`).html(content_loading).addClass(`disabled`);

            const result = await ajax.post(`/serial_list`, {port: selectedPort});
            console.log(result);

            if (result.result == `ok`) {
                proceedToDashboard();
            }
        });
    } catch (e) {
        console.log(e);
    }
};

const proceedToDashboard = async () => {
    console.log(`proceedToDashboard start!`);

    hideEveryThing();
    $(`#room-cards-container`).show();
    const roomQueryTimeRange = {};

    // update cards
    const updateCards = async () => {
        const status = await ajax.get(`/status`);

        if (status && status.data) {
            let rebindEvents = false;

            for (const roomId in status.data) {
                const roomCard = $(`#room-card-${roomId}`);

                if (roomCard.length == 0) {
                    rebindEvents = true;

                    // create new card
                    let roomCardsHtml = $(`#room-cards-container`).html();
                    if (roomCardsHtml.trim()) {
                        roomCardsHtml += `<hr />`
                    }

                    roomCardsHtml += room_card(roomId);
                    $(`#room-cards-container`).html(roomCardsHtml);
                }

                let sensorHtml = `Sensors: <br />`;

                for (const sensorId in status.data[roomId]) {
                    if (sensorId == `ts`) {
                        sensorHtml += `<b>Last update</b>: ${formatDateTime(new Date(status.data[roomId][sensorId]))} <br />`
                    } else {
                        sensorHtml += `<b>${sensorId}</b>: ${status.data[roomId][sensorId]} <br />`
                    }
                }

                $(`#room-card-${roomId} .card-text`).html(sensorHtml);
            }

            if (rebindEvents) {
                // initialize components
                $(`.room-card .start-dt`).daterangepicker({
                    timePicker: true,
                    startDate: moment().startOf('hour'),
                    endDate: moment().startOf('hour').add(32, 'hour'),
                    locale: {
                        format: 'M/DD hh:mm A'
                    }
                }).on(`apply.daterangepicker`, (event, picker) => {
                    const roomId = $(event.target).attr(`room-id`);
                    console.log(`${roomId}.startDate = ${picker.startDate}`);
                    console.log(`${roomId}.endDate = ${picker.endDate}`);

                    roomQueryTimeRange[roomId] = {
                        startDate: picker.startDate,
                        endDate: picker.endDate
                    }

                    $(`#room-card-${roomId} .btn-run-query`).removeClass(`disabled`);
                }).val(`select a date/time range...`);

                $(`.room-card .btn-start-query`).click((event) => {
                    const roomId = $(event.target).attr(`room-id`);
                    $(`#room-card-${roomId} .query_table`).show();
                    $(event.target).hide();
                });

                $(`.room-card .btn-close-query`).click((event) => {
                    const roomId = $(event.target).attr(`room-id`);
                    $(`#room-card-${roomId} .query_table`).hide();
                    $(`#room-card-${roomId} .btn-start-query`).show();
                });

                $(`.room-card .btn-run-query`).click(async (event) => {
                    const roomId = $(event.target).attr(`room-id`);
                    $(`#room-card-${roomId} .btn-run-query`).addClass(`disabled`).html(content_loading);
                    const queryTimeRange = roomQueryTimeRange[roomId];

                    const payload = {
                        room_id: roomId,
                        ts_start: queryTimeRange.startDate._d.getTime(),
                        ts_end: queryTimeRange.endDate._d.getTime()
                    }

                    const result = await ajax.post(`/query`, payload);

                    let queryTableContent = ``;
                    if (result && result.result && result.result.length > 0) {
                        const rows = result.result;
                        for (let i = 0; i < rows.length; i++) {
                            queryTableContent += queryTableItem(rows[i].sensor_id, rows[i].value, rows[i].ts);
                        }
                    }
                    $(`#room-card-${roomId} .query_table tbody`).html(queryTableContent);

                    $(`#room-card-${roomId} .btn-run-query`).removeClass(`disabled`).html(`Query`);
                });
            }
        }

        setTimeout(updateCards, 1000);
    };

    // start scheduled task
    await updateCards();
};