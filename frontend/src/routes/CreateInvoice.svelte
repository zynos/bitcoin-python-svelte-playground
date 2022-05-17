<script>
    import JSONTree from "svelte-json-tree";
    import { onMount } from "svelte";
    import QRCode from "./QRJS.svelte";
    import Dummy_qr from "./Dummy_qr.svelte";
  
    let sat_mount = 10;
    let invoice_data = {};
    let payment_request = "";
    let settled = true;
    let invoice_index = -1;
    let message_after_payment = "";
    let interval = null;
  
    let value;
  
    async function getInvoice() {
      const url = "http://localhost:8000/invoice/" + sat_mount;
      console.log(url);
      const response = await fetch(url);
      invoice_data = await response.json();
      console.log(invoice_data);
      payment_request = invoice_data["paymentRequest"];
      invoice_index = invoice_data["addIndex"];
      console.log(payment_request);
      value = invoice_data
      interval = setInterval(checkInvoicePayed, 3000);
      return payment_request;
    }
  
    async function checkInvoicePayed() {
      // const url = "http://localhost:8000/invoice_paid/" + 49;
      const url = "http://localhost:8000/invoice_paid/"+invoice_index;
  
      console.log(url);
      const response = await fetch(url);
      invoice_data = await response.json();
      console.log(invoice_data);
      settled = invoice_data["settled"];
      console.log(settled);
      if (settled == true) {
        clearInterval(interval);
        console.log("inside if");
      }
  
      console.log(settled);
      return settled;
    }
  </script>
  
  

  
  <h1>You pay {sat_mount} satoshis</h1>
  <input bind:value={sat_mount} />
  <button on:click={getInvoice}>Get Invoice QR</button>
  <br />
  <button on:click={checkInvoicePayed}>Check Invoice paid</button>
  <input bind:value={settled} />
  <br />
  
  {#if payment_request != ""}
    <h3>
      Use third party lib like <a href="https://davidshimjs.github.io/qrcodejs/"
        >QRcodeJS</a
      >
    </h3>
    <QRCode codeValue={payment_request} squareSize="300" />
    <h3>Or youse img tag with data from backend!</h3>
    <img src= {value["payment_request_qr"]} alt="your qrcode" width="300" height="300"/>
    {:else}
    <p>Loading invoice..</p>
    <p>{payment_request}</p>

  {/if}

  
  {#if invoice_index > -1}
    <h1>{message_after_payment}</h1>
  {/if}
  