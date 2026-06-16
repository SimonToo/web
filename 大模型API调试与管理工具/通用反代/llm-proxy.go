package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"regexp"
	"strings"
	"time"
)

var doubleSlashRE = regexp.MustCompile(`^(https?:)/+(.*)$`)

var proxyClient *http.Client

func init() {
	transport := &http.Transport{
		DialContext: (&net.Dialer{
			Timeout:   120 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		ResponseHeaderTimeout: 120 * time.Second,
		DisableCompression:    true,
	}
	proxyClient = &http.Client{Transport: transport}
}

func main() {
	printBanner()

	if err := http.ListenAndServe(":8317", corsMiddleware(http.HandlerFunc(routerHandler))); err != nil {
		fmt.Printf("❌ 服务启动失败: %v\n", err)
	}
}

// routerHandler bypasses http.ServeMux to avoid automatic path.Clean
// which collapses "//" → "/" and causes 301 redirects that break POST.
func routerHandler(w http.ResponseWriter, r *http.Request) {
	if strings.HasPrefix(r.URL.Path, "/proxy/") {
		proxyHandler(w, r)
		return
	}
	if r.URL.Path == "/proxy" {
		writeError(w, http.StatusBadRequest, "请在 /proxy/ 后附上目标 URL，例如 /proxy/https://api.openai.com/v1")
		return
	}
	writeError(w, http.StatusNotFound, "Not Found")
}

func printBanner() {
	fmt.Println(strings.Repeat("=", 65))
	fmt.Println(" 🚀 大模型万能通用跨域反向代理已启动")
	fmt.Println(" 监听端口 : 8317")
	fmt.Println(" 配置方式 : 在网页端 AI 设置中，将原来的真实 Base URL 替换为：")
	fmt.Println("            http://localhost:8317/proxy/真实的Base_URL")
	fmt.Println(" 示例地址 : http://localhost:8317/proxy/https://api.openai.com/v1")
	fmt.Println(strings.Repeat("=", 65))
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "*")
		w.Header().Set("Access-Control-Allow-Headers", "*")
		w.Header().Set("Access-Control-Allow-Credentials", "true")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func proxyHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("-> %s %s", r.Method, r.URL.String())

	targetURL := strings.TrimPrefix(r.URL.Path, "/proxy/")
	if targetURL == "" || targetURL == r.URL.Path {
		writeError(w, http.StatusBadRequest, "请在 /proxy/ 后附上目标 URL，例如 /proxy/https://api.openai.com/v1")
		return
	}

	targetURL = doubleSlashRE.ReplaceAllString(targetURL, "$1//$2")

	if r.URL.RawQuery != "" {
		targetURL += "?" + r.URL.RawQuery
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		writeError(w, http.StatusBadGateway, "读取请求体失败")
		return
	}
	r.Body.Close()

	upstreamReq, err := http.NewRequest(r.Method, targetURL, bytes.NewReader(body))
	if err != nil {
		writeError(w, http.StatusBadRequest, fmt.Sprintf("无效的目标 URL: %s", err.Error()))
		return
	}

	for key, vals := range r.Header {
		switch key {
		case "Host", "Content-Length", "Origin", "Referer", "Accept-Encoding":
			continue
		}
		for _, v := range vals {
			upstreamReq.Header.Add(key, v)
		}
	}

	resp, err := proxyClient.Do(upstreamReq)
	if err != nil {
		writeError(w, http.StatusBadGateway, fmt.Sprintf("代理连接失败: %s", err.Error()))
		return
	}
	defer resp.Body.Close()

	if ct := resp.Header.Get("Content-Type"); ct != "" {
		w.Header().Set("Content-Type", ct)
	}
	w.WriteHeader(resp.StatusCode)

	flusher, ok := w.(http.Flusher)
	if !ok {
		io.Copy(w, resp.Body)
		return
	}

	buf := make([]byte, 32*1024)
	for {
		n, err := resp.Body.Read(buf)
		if n > 0 {
			w.Write(buf[:n])
			flusher.Flush()
		}
		if err != nil {
			if err == io.EOF {
				break
			}
			return
		}
	}
}

func writeError(w http.ResponseWriter, status int, msg string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]string{"error": msg})
}
