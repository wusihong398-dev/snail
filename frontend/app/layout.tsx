import "./globals.css";
import Providers from "./providers";

export const metadata = {
  title: "蜗牛群聊精灵后台",
  description: "AI微信群互动机器人管理平台",
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  return (
    <html lang="zh-CN">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
