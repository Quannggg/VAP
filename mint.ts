import { Connection, PublicKey, clusterApiUrl } from "@solana/web3.js";
import {
  Metaplex,
  bundlrStorage,
  toMetaplexFile,
  toBigNumber,
} from "@metaplex-foundation/js";
import * as fs from "fs";

const QUICKNODE_RPC = "https://api.devnet.solana.com";
const SOLANA_CONNECTION = new Connection(QUICKNODE_RPC);
const METAPLEX = Metaplex.make(SOLANA_CONNECTION).use(
  bundlrStorage({
    address: "https://devnet.bundlr.network",
    providerUrl: QUICKNODE_RPC,
    timeout: 60000,
  })
);

export interface Config {
  uploadPath: string;
  imgFileName: string;
  imgType: string;
  imgName: string;
  description: string;
  attributes: { trait_type: string; value: string }[];
  sellerFeeBasisPoints: number;
  symbol: string;
  creators: { address: PublicKey; share: number }[];
}

export async function uploadImage(
  filePath: string,
  fileName: string
): Promise<string> {
  console.log(`Step 1 - Uploading Image`);
  const imgBuffer = fs.readFileSync(filePath + fileName);
  const imgMetaplexFile = toMetaplexFile(imgBuffer, fileName);
  const imgUri = await METAPLEX.storage().upload(imgMetaplexFile);
  console.log(`   Image URI:`, imgUri);
  return imgUri;
}

export async function uploadMetadata(
  imgUri: string,
  imgType: string,
  nftName: string,
  description: string,
  attributes: { trait_type: string; value: string }[]
) {
  console.log(`Step 2 - Uploading Metadata`);
  const { uri } = await METAPLEX.nfts().uploadMetadata({
    name: nftName,
    description: description,
    image: imgUri,
    attributes: attributes,
    properties: {
      files: [
        {
          type: imgType,
          uri: imgUri,
        },
      ],
    },
  });
  console.log("   Metadata URI:", uri);
  return uri;
}

export async function mintNft(
  metadataUri: string,
  name: string,
  sellerFee: number,
  symbol: string,
  creators: { address: PublicKey; share: number }[]
) {
  console.log(`Step 3 - Minting NFT`);
  const { nft } = await METAPLEX.nfts().create({
    uri: metadataUri,
    name: name,
    sellerFeeBasisPoints: sellerFee,
    symbol: symbol,
    creators: creators,
    isMutable: false,
    maxSupply: toBigNumber(1),
  });
  console.log(
    `   Minted NFT: https://explorer.solana.com/address/${nft.address}?cluster=devnet`
  );
}
