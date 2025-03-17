import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";


// Ensure the output directory exists
const outputDir = 'boids_output';
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

// Example function to save data to a JSON file
function saveDataToFile(N, max, cohesion, separation, alignment, inner, outer, data) {
    const filename = `output_${cohesion}_${separation}_${alignment}.json`;
	const foldername = `output_${N}_${max}_${inner}_${outer}`
	const folderDir = path.join(outputDir, foldername)
	if (!fs.existsSync(folderDir)) {
		fs.mkdirSync(folderDir, { recursive: true });
	}
    const filePath = path.join(folderDir, filename);

    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        console.log(`Data saved to ${filePath}`);
    } catch (err) {
        console.error(`Error saving data to ${filePath}:`, err);
    }
}

let canvas, S
let conf = {
	w : 400,
	h : 400,
	N : 200, 
	zoom : 1,
	innerRadius : 10,
	outerRadius : 25,
	cohesion : 1,
	separation : 1,
	alignment : 1
}


class Canvas {
	constructor( Scene, conf ){
		this.zoom = conf.zoom
		this.S = Scene
		this.height = this.S.h
		this.width = this.S.w
		this.el = document.createElement("canvas")
		this.el.width = this.width*this.zoom
		this.el.height = this.height*this.zoom
		let parent_element = document.getElementById( "canvasModel" ) 
		parent_element.appendChild( this.el )
		
		this.ctx = this.el.getContext("2d")
		this.ctx.lineWidth = .2
		this.ctx.lineCap="butt"
		
	}
	
	background( col ){
		col = col || "000000"
		this.ctx.fillStyle="#"+col
		this.ctx.fillRect( 0,0, this.el.width, this.el.height )
	}
	
	fillCircle( pos, col ){
		this.ctx.fillStyle="#"+col
		this.ctx.beginPath()
		this.ctx.arc( pos[0], pos[1], this.S.conf.innerRadius/2, 0, 2 * Math.PI )
		this.ctx.stroke()
		this.ctx.fill()
	}
	
	drawCircle( pos, col, radius ){
		this.ctx.lineWidth = .5*this.zoom
		this.ctx.strokeStyle="#"+col
		this.ctx.beginPath()
		this.ctx.arc( pos[0], pos[1], radius * this.zoom, 0, 2 * Math.PI )
		this.ctx.stroke()
	}
	
	drawDirections(){
		this.ctx.strokeStyle="#000000"
		const ctx = this.ctx, zoom = this.zoom
		ctx.beginPath()
		ctx.lineWidth = 2*zoom
	
		for( let p of this.S.swarm ){
			
			const startPoint = p.multiplyVector( p.pos, zoom )
			
			let drawVec = p.multiplyVector( p.dir, this.S.conf.innerRadius * 1.2 * zoom )
			drawVec = p.addVectors( startPoint, drawVec )
				
			ctx.moveTo( startPoint[0], startPoint[1] )
			ctx.lineTo( drawVec[0], drawVec[1] )
		}
		ctx.stroke()		
	}
	
	drawSwarm(){
		this.background( "eaecef" )
		for( let p of this.S.swarm ){
			this.fillCircle( p.pos, "ff0000" )
			this.drawCircle( p.pos, "aaaaaa", this.S.conf.outerRadius )
		}
		this.drawDirections()
	}	
}

class Scene {
	
	constructor( conf ){
		this.w = conf.w
		this.h = conf.h 
		this.conf = conf
		this.swarm = []
		this.makeSwarm()
		this.time = 0
	}
	
	reset(){
		this.swarm = []
		this.time = 0
		this.makeSwarm()
	}
	
	getAngles(){
		let angles = []
		for( let p of this.swarm ){
			const ang = 180 + (180/Math.PI) * Math.atan2( p.dir[1], p.dir[0] )
			angles.push( ang )
		}
		return angles
	}
	
	wrap( pos, reference = undefined ){
	
		// wrapping without a reference: just make sure the coordinate falls within 
		// the space
		if( (typeof reference == 'undefined') ){
		
			if( pos[0] < 0 ) pos[0] += this.w
			if( pos[1] < 0 ) pos[1] += this.h
			if( pos[0] > this.w ) pos[0] -= this.w
			if( pos[1] > this.h ) pos[1] -= this.h
	
			return pos
		}

		// otherwise: make coordinates consistent compared to a reference position
		// we don't want to overwrite the 'pos' object itself (!JavaScript) so deep copy it first
		const pos2 = pos.slice()
		let dx =  pos2[0] - reference[0] , dy = pos2[1] - reference[1]
		if( dx > this.w/2 ) pos2[0] -= this.w
		if( dx < -this.w/2 ) pos2[0] += this.w
		if( dy > this.h/2 ) pos2[1] -= this.h
		if( dy < -this.h/2 ) pos2[1] += this.h
		
		
		return pos2
		
	}
	
	addParticle(){
		const i = this.swarm.length + 1
		this.swarm.push( new Particle( this, i ) )
	}
	
	makeSwarm(){
		for( let i = 0; i < this.conf.N; i++ ) this.addParticle()
	}
	
	randomPosition(){
		let x = Math.random() * this.w
		let y = Math.random() * this.h
		return [x,y]
	}
	
	randomDirection( dim = 2 ){
		let dir = []
		while(dim-- > 0){
			dir.push(this.sampleNorm())
		}
		this.normalizeVector(dir)
		return dir
	}
	
	normalizeVector( a ){
	
		if( a[0] == 0 & a[1] == 0 ) return [0,0]
	
		let norm = 0
		for( let i = 0 ; i < a.length ; i ++ ){
			norm += a[i]*a[i]
		}
		norm = Math.sqrt(norm)
		for( let i = 0 ; i < a.length ; i ++ ){
			a[i] /= norm
		}
		return a
	}
	
	sampleNorm(mu=0, sigma=1) {
		let u1 = Math.random()
		let u2 = Math.random()
		let z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(Math.PI*2 * u2)
		return z0 * sigma + mu
	}
	
	dist( pos1, pos2 ){
	
		let dx = pos1[0] - pos2[0]
		if( dx > this.w/2 ){ dx -= this.w }
		if( dx < (-this.w/2) ){ dx += this.w }
		
		let dy = pos1[1] - pos2[1]
		if( dy > this.h/2 ){ dy -= this.h }
		if( dy < ( -this.h/2 ) ){ dy += this.h }
		
		const dist = Math.sqrt( dx * dx + dy * dy )
		return dist
		//const dist = Math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1] )	
	}
	
	neighbours( x, distanceThreshold ){
		let r = []
		for( let p of this.swarm ){
			if( p.id == x.id ) continue 
			
			if( this.dist( p.pos, x.pos ) <= distanceThreshold ){
				r.push( p )
			}
		}
		return r
	}	
	
    getNeighboursDist(){
		let dists = []
		for( let p of this.swarm ){
       		 // Calculate distances to all neighbors
        	let dists_int = this.neighbours(p, this.conf.outerRadius).map(x => this.dist(x.pos, p.pos));
       		 // Add distances to the main array
			let dists_int2 = 0
			let count = 0
			if (dists_int.length > 0){
        		for (let d of dists_int){
					if (d != NaN){
						dists_int2 += d
						count++
					}
				}
				dists.push(dists_int2/count)
			}
			else{
				dists.push(0)
			}
    	}	
		let mean = dists.reduce((a, b) => a + b) / dists.length
		let variance = dists.reduce((a, b) => a + (b - mean) ** 2) / dists.length
        return {means: mean, variances: variance}
    }   

	step(){
		for( let p of this.swarm ){
			p.updateVector()
		}
		this.time++
	}
}



class Particle {
	constructor( Scene, i ){
		this.S = Scene
		this.speed = 1 
		this.id = i
		this.pos = this.S.randomPosition() 
		this.dir = this.S.randomDirection()
	}
	// return a + b
	addVectors( a, b ){
		const dim = a.length
		let out = []
		for( let d = 0; d < dim; d++ ){
			out.push( a[d] + b[d] )
		}
		return out
	}
	// return a - b
	subtractVectors( a, b ){
		const dim = a.length
		let out = []
		for( let d = 0; d < dim; d++ ){
			out.push( a[d] - b[d] )
		}
		return out
	}
	// multiply vector by a constant
	multiplyVector( a, c ){
		return a.map(( x ) => x * c ) 
	}
	// normalize vector to unit length
	normalizeVector( a ){
		return this.S.normalizeVector(a)
	}
	
	// should return a unit vector in average neighbor direction for neighbors within 
	// distance neighborRadius 
	alignmentVector( neighborRadius ){
		let sum = [0,0]	
		let counter = 0
		// loop over all neighbours in neighborRadius
		for (let n of this.S.neighbours(this, neighborRadius)){
			// add the direction of the neighbor
			sum = this.addVectors(sum, n.dir)
		}		
		if (counter == 0){
			return [0,0]
		}
		else{
			sum.map(i => i/counter)
			return this.subtractVectors(sum, this.dir )
		}
	
	}
	
	// should return a unit vector in the direction from current position to the 
	// average position of neighbors within distance neighborRadius 
	cohesionVector( neighborRadius ){
		let sum = [0,0]
		let counter = 0
		// loop over all neighbours in neighborRadius
		for (let n of this.S.neighbours(this, neighborRadius)){
			// add the position of the neighbor
			sum = this.addVectors(sum, n.pos)
			counter++
		}
		if (counter == 0){
			return [0,0]
		}
		else{
			sum.map(i => i/counter)
			return this.subtractVectors(sum, this.pos)
		}
	
	}
	
	// as cohesionVector, but now return the opposite direction for the given 
	separationVector( neighborRadius ){
		let sum = [0,0]
		let counter = 0	
		// loop over all neighbours in neighborRadius
		for (let n of this.S.neighbours(this, neighborRadius)){
			// add the position of the neighbor
			sum = this.addVectors(sum, this.pos-n.pos)
			counter++
		}
		if (counter == 0){	
			return [0,0]
		}
		else{
			return this.normalizeVector(this.subtractVectors(sum, this.pos))
		}
	}
	

	updateVector(){
		
		let align_weight = this.S.conf.alignment
		let cohesion_weight = this.S.conf.cohesion
		let separation_weight = this.S.conf.separation
		
		const align = this.multiplyVector( this.alignmentVector( this.S.conf.outerRadius ), align_weight )
		const cohesion = this.multiplyVector(this.cohesionVector( this.S.conf.outerRadius ), cohesion_weight )
		const separation = this.multiplyVector( this.separationVector(this.S.conf.innerRadius), separation_weight )
		
		
		this.dir = this.addVectors( this.dir, align )
		this.dir = this.addVectors( this.dir, cohesion )
		this.dir = this.addVectors( this.dir, separation )
		this.dir = this.normalizeVector( this.dir )
		this.pos = this.S.wrap( this.addVectors( this.pos, this.multiplyVector( this.dir, this.speed ) ) )

	}
	
}



function initialize(){
	
	S = new Scene( conf )
	canvas = new Canvas( S, conf )
	// canvas.drawSwarm()
	
	let angles = []

	let trace = {
		x: angles,
		type: 'histogram',
	  };
	let  data = [trace]
	var layout = {
	  xaxis: {range: [0, 2*Math.PI]}
	};
	Plotly.newPlot( 'myDiv', data, layout);


	
}

function simulate(max_iter = 5000){
	let order = []
    let dist_mean= []
	let dist_var = []
	let S = new Scene( conf )
	// initialize()
	for (let i = 0; i < max_iter; i++){
		S.step()
        // push average normalised angle
		let angles = S.getAngles()
		// console.log(angles)
		if (angles.length > 0) {
			let order_int = 0
			let i = 0
			for (let a of angles){
				// console.log(a)
				if (Object.is(NaN, a)){
					continue
				}
				else{
					order_int += a
					i += 1
				}
			}
			// console.log(order_int)
			order.push(order_int/ i);
        } else {
            order.push(0); // Handle case where no angles are available
        }


        // push average distance and variance
        let dists = S.getNeighboursDist()
		let mean = dists.means
		let variance = dists.variances
		dist_mean.push(mean)
		dist_var.push(variance)
		// check if converged
		if (S.swarm.length == 1){
			console.log("Converged at "  + i + " iterations")
            iter_conv = i
			return [order, dist_mean, dist_var, iter_conv, S.getAngles().length]
		}
        else if(i == max_iter-1){
            console.log("Not converged")
            return [order, dist_mean, dist_var, max_iter, S.getAngles().length]
        }
	}
}






if (process.argv[1] === fileURLToPath(import.meta.url)) {
    let N = process.argv[2]
    let i = process.argv[3]
    let j = process.argv[4]
    let k = process.argv[5]
	let max = process.argv[6]
	let inner = process.argv[7]
	let outer = process.argv[8]
	let config = {	
		w : 400,
		h : 400,
		N  : N,
		zoom : 1,
		innerRadius : inner,
		outerRadius : outer,
		cohesion : i/max,
		separation : j/max,
		alignment : k/max
	}
	let conf = config	
	let [order, dist_mean, dist_var, conv_iter, N_fin] = simulate();

	// save outputs into JSON dictionary
    let output = {
        "order_parameter": order,
		"dist_mean": dist_mean,
		"dist_var": dist_var,
        "converged": conv_iter,
        "N": N_fin
    }
	saveDataToFile(N, max, i, j, k, inner, outer, output)
}