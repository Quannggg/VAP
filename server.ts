import { Connection, PublicKey, clusterApiUrl } from "@solana/web3.js";
import express, { Request, Response } from "express";

const app = express();

async function checkBalance(addressStr: string): Promise<number> {
    const connection = new Connection(clusterApiUrl("devnet"));
    const address = new PublicKey(addressStr);
    const balance = await connection.getBalance(address);
    return balance / 10**9; // Convert lamports to SOL
}

app.get("/balance/:address", async (req: Request, res: Response) => {
    const address = req.params.address as string;
    try {
        const balance = await checkBalance(address);
        res.json({balance });
    } catch (error) {
        res.status(500).json({ error: "Failed to get balance" });
    }
});

const port = 3000;
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
