import './globals.css';

export const metadata = {
  title: 'OZ Report Generator',
  description: 'XLSX 파일을 업로드하면 OZ Report (.ozr/.odi) 파일을 자동 생성합니다.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
