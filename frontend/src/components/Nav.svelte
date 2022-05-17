<script>
    import NavLink from "./NavLink.svelte";
</script>

<nav>
    <ul>
        <li><NavLink href="/" title="Home" /></li>
        <li><NavLink href="/CreateInvoice" title="Create Invoice" /></li>
        <li><NavLink href="/Dummy_qr" title="Dummy Invoice" /></li>
        <li><NavLink href="/Mempool" title="Mempool" /></li>
    </ul>
</nav>

<style>
    ul {
        list-style-type: none;
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: #333;
    }

    li {
        float: left;
    }

    li a {
        display: block;
        color: white;
        text-align: center;
        padding: 14px 16px;
        text-decoration: none;
    }

    li a:hover:not(.active) {
        background-color: #111;
    }

    .active {
        background-color: #04aa6d;
    }
</style>
