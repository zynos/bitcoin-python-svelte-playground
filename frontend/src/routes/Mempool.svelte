<script>
  import JSONTree from "svelte-json-tree";
  import { onMount } from "svelte";

  let value;

  onMount(async () => {
    await fetch("http://localhost:8000/")
      .then((r) => r.json())
      .then((data) => {
        console.log(data);
        value = data;
      });
  });
</script>

<h1>Mempool</h1>
<JSONTree {value} />
