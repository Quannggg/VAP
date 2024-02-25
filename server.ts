import { Connection, PublicKey, clusterApiUrl } from "@solana/web3.js";
import express, { Request, Response } from "express";
import { Config, mintNft, uploadImage, uploadMetadata } from "./mint";

const app = express();

async function checkBalance(addressStr: string): Promise<number> {
  const connection = new Connection(clusterApiUrl("devnet"));
  const address = new PublicKey(addressStr);
  const balance = await connection.getBalance(address);
  return balance / 10 ** 9; // Convert lamports to SOL
}

app.get("/balance/:address", async (req: Request, res: Response) => {
  const address = req.params.address as string;
  try {
    const balance = await checkBalance(address);
    res.json({ balance });
  } catch (error) {
    res.status(500).json({ error: "Failed to get balance" });
  }
});
import axios from "axios";

// export async function uploadImageFromUrl(
//   imageUrl: string,
//   fileName: string
// ): Promise<string> {
//   console.log(`Step 1 - Uploading Image from URL`);
//   const response = await axios.get(imageUrl, {
//     responseType: "arraybuffer",
//   });
//   const imgBuffer = Buffer.from(response.data, "binary");
//   const imgMetaplexFile = toMetaplexFile(imgBuffer, fileName);
//   const imgUri = await METAPLEX.storage().upload(imgMetaplexFile);
//   console.log(`   Image URI:`, imgUri);
//   return imgUri;
// }

const CONFIG: Config = {
  uploadPath: "uploads/",
  imgFileName: "image.png",
  imgType: "image/png",
  imgName: "QuickNode Pixel",
  description: "Pixel infrastructure for everyone!",
  attributes: [
    { trait_type: "Speed", value: "Quick" },
    { trait_type: "Type", value: "Pixelated" },
    { trait_type: "Background", value: "QuickNode Blue" },
  ],
  sellerFeeBasisPoints: 500, //500 bp = 5%
  symbol: "QNPIX",
  creators: [{ address: new PublicKey("PUBLIC_KEY"), share: 100 }], // Replace with your public key
};

app.get("/mint-nft", async (req: Request, res: Response) => {
  try {
    console.log(`Minting ${CONFIG.imgName} to an NFT`);
    // Step 1 - Upload Image
    const imgUri = await uploadImage(CONFIG.uploadPath, CONFIG.imgFileName);
    // Step 2 - Upload Metadata
    const metadataUri = await uploadMetadata(
      imgUri,
      CONFIG.imgType,
      CONFIG.imgName,
      CONFIG.description,
      CONFIG.attributes
    );
    // Step 3 - Mint NFT
    await mintNft(
      metadataUri,
      CONFIG.imgName,
      CONFIG.sellerFeeBasisPoints,
      CONFIG.symbol,
      CONFIG.creators
    );
    res.status(200).json({ message: "NFT minted successfully" });
  } catch (error) {
    console.error("Error minting NFT:", error);
    res.status(500).json({ error: "Failed to mint NFT" });
  }
});

const port = 3000;
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
