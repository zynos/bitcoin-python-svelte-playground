<script>
  import { onMount } from "svelte";

	let value = null;
    onMount(async () => {
      console.log("try fetch");
    await fetch("http://localhost:8000/get_dummy_invoice/")
      .then(r => r.json())
      .then(data => {
          console.log(data);
        value = data;
      });
      });


</script>

<h1>Request Dummy Invoice QR from backend</h1>
{#if value}

<img src= {value["payment_request_qr"]} alt="your qrcode" width="300" height="300"/>
<br>
<span style="width:300px; word-wrap:break-word; display:inline-block;"> 
   {value["payment_request"]}
</span>
{:else}
<p> Please check if your backend is running</p>
{/if}